from ._mocks import Transform
from .core import CameraDataReader, FrameDataReader


class PlaybackAgent:
    """Mock agent class that can be used to playback data."""

    __slots__ = [
        "_frame_data",
        "_camera_data",
        "_frame",
        "_frame_data_row",
        "_max_frame",
    ]

    def __init__(self, data_path: str):
        """Initialize the playback agent.

        Args:
            data_path: The path to the data file.
        """

        # Data Readers
        self._frame_data = FrameDataReader(data_path)
        self._camera_data = CameraDataReader(data_path)

        # Initialize at the first frame
        self._frame = self._frame_data.frames["frame"].min()
        self._frame_data_row = self._frame_data[self._frame]

        # Set the max frame number
        self._max_frame = self._frame_data.frames["frame"].max()

    def set_frame(self, frame: int):
        """Jump to a specific frame.

        Args:
            frame: The frame to set the agent to.
        """

        # Check if the frame is inside the range of the data
        if frame > self._max_frame:
            raise ValueError(
                f"Frame {frame} is out of range. Max index is {self._max_frame}."
            )

        # Try to set the frame data row
        try:
            self._frame_data_row = self._frame_data[frame]
            self._frame = frame
        except KeyError:
            raise ValueError(f"Frame {frame} is not in the data set.")

    def at_end(self) -> bool:
        """Check if the agent is at the end of the data set."""
        return self._frame == self._max_frame

    def step_frame(self) -> int:
        """Step to the next frame in the data set. Stops at the last frame.

        Returns:
            The new frame number.
        """

        # Step to the next frame in the data set
        try:
            self._frame = (
                self._frame_data.frames[self._frame_data.frames["frame"] > self._frame]
                .iloc[0]
                .to_dict()["frame"]
            )
        except IndexError:
            pass

        self._frame_data_row = self._frame_data[self._frame]
        return self._frame

    def input_data(self) -> dict:
        """Get the input data for the current frame."""
        return self._camera_data.input_data(self._frame)

    # Constant Functions
    def use_fiducials(self) -> bool:
        return self._frame_data.initial["fiducials"]

    def sensors(self) -> dict:
        return self._frame_data.initial["cameras"]

    def get_initial_position(self) -> Transform:
        return Transform(
            p=self._frame_data.initial["rover"][:3],
            e=self._frame_data.initial["rover"][3:],
        )

    def get_initial_lander_position(self) -> Transform:
        return Transform(
            p=self._frame_data.initial["lander"][:3],
            e=self._frame_data.initial["lander"][3:],
        )

    # Frame Dependent Functions
    def get_mission_time(self) -> float:
        return self._frame_data_row["mission_time"]

    def get_current_power(self) -> float:
        return self._frame_data_row["power"]

    def get_consumed_power(self) -> float:
        raise NotImplementedError("get_consumed_power not implemented")

    def get_imu_data(self) -> list:
        data = []
        data.append(self._frame_data_row["accel_x"])
        data.append(self._frame_data_row["accel_y"])
        data.append(self._frame_data_row["accel_z"])
        data.append(self._frame_data_row["gyro_x"])
        data.append(self._frame_data_row["gyro_y"])
        data.append(self._frame_data_row["gyro_z"])
        return data

    def get_linear_speed(self) -> float:
        return self._frame_data_row["linear_speed"]

    def get_angular_speed(self) -> float:
        return self._frame_data_row["angular_speed"]

    def get_front_arm_angle(self) -> float:
        raise NotImplementedError("get_front_arm_angle not implemented")

    def get_back_arm_angle(self) -> float:
        raise NotImplementedError("get_back_arm_angle not implemented")

    def get_front_drums_speed(self) -> float:
        raise NotImplementedError("get_front_drums_speed not implemented")

    def get_back_drums_speed(self) -> float:
        raise NotImplementedError("get_back_drums_speed not implemented")

    def get_radiator_cover_angle(self) -> float:
        return self._frame_data_row["cover_angle"]

    def get_transform(self) -> Transform:
        translation = [
            self._frame_data_row["x"],
            self._frame_data_row["y"],
            self._frame_data_row["z"],
        ]
        rotation = [
            self._frame_data_row["roll"],
            self._frame_data_row["pitch"],
            self._frame_data_row["yaw"],
        ]
        return Transform(p=translation, e=rotation)

    # Camera Functions
    def get_light_state(self, camera: str) -> float:
        try:
            return self._camera_data.get_frame(camera, self._frame, True)[
                "light_intensity"
            ]
        except (ValueError, TypeError):
            # The camera was never enabled, so we can just return the initial value
            return self._frame_data.initial["cameras"][camera]["light_intensity"]

    def get_camera_state(self, camera: str) -> bool:
        try:
            return self._camera_data.get_frame(camera, self._frame, True)["enable"]
        except (ValueError, TypeError):
            # ValueError: The camera was never enabled
            # TypeError: There was no camera data for this frame
            return False

    def get_camera_position(self, camera: str) -> Transform:
        try:
            row = self._camera_data.get_frame(camera, self._frame, True)
            translation = [row["camera_x"], row["camera_y"], row["camera_z"]]
            rotation = [row["camera_roll"], row["camera_pitch"], row["camera_yaw"]]
            return Transform(p=translation, e=rotation)

        except (ValueError, TypeError):
            # The camera was never enabled
            # TODO: This could also return the initial camera positions from the rover geometry
            return Transform(
                p=[0.0, 0.0, 0.0],
                e=[0.0, 0.0, 0.0],
            )

    def get_light_position(self, camera: str) -> Transform:
        # TODO: Add a fixed offset for the light position
        raise NotImplementedError("get_light_position not implemented")
