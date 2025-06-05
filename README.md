# LunarLoc
Data and replay utilities for [LunarLoc]().

# Datasets
Seventeen individual traverses are provided in two data formats: `.csv` and `.lac`.
Due to their size, `.lac` files are not included in this repository and can be found under [releases](https://github.com/Robaire/LunarLoc/releases).

## CSV
Included `.csv` files contain only the rover's ground truth x, y, z position and any estimated boulder detections in the scene for each frame.

## LAC
Included `.lac` files contain more detailed information, including the rover's ground truth 6-DOF pose, IMU data, rover configuration state, and camera images from the simulator. 
Python utilities to access the contents of `.lac` files are included in this repository.
Alternatively, `.lac` files are `.tar.gz` archives and can be extracted with `tar -xzf <file_name>.lac` if desired.
The internal structure of the archive is defined below.

```text
<file_name>.lac/
├── metadata.toml 
├── initial.toml 
├── frames.csv 
├── images/ 
│   └── <camera>/ 
│       ├── <camera>_frames.csv 
│       ├── grayscale/ 
│       │   └── <camera>_grayscale_<frame>.png 
│       └── semantic/ 
│           └── <camera>_semantic_<frame>.png 
└── custom/ 
    └── <record_name>.csv
```

# Reading Data
Sample data and an example playback script are included in `examples`.
Code is adapted from [lac-data](https://github.com/Robaire/lac-data).
Two core classes, `FrameDataReader` and `CameraDataReader` are provided to access the numeric and image data from a `.lac` file.
An additional `PlaybackAgent` is provided to mock agent behavior synchronized to a `.lac` file.

## FrameDataReader
The `FrameDataReader` provides direct access to [pandas](https://pandas.pydata.org/) `DataFrame`s for numerical data.

```python
reader = FrameDataReader("./examples/example.lac")
reader.initial -> dict
reader.frames -> pd.DataFrame
reader.camera_frames -> dict[str, pd.DataFrame]
reader.custom_records -> dict[str, pd.DataFrame]
```

## CameraDataReader
The `CameraDataReader` provides access to camera specific numerical data and image data.
Images are provided as [numpy](https://numpy.org/) arrays.

```python
reader = CameraDataReader("./examples/example.lac")
reader.get_frame("FrontLeft", 20) -> dict
reader.get_image("FrontLeft", 20, "grayscale") -> np.ndarray

# Get a LAC style input_data dictionary
reader.input_data(20) -> dict 
```

## PlaybackAgent
`PlaybackAgent` mocks the functionality of the `AutonomousAgent` base class from the [Lunar Autonomy Challenge](https://lunar-autonomy-challenge.jhuapl.edu/).
The agent provides most of the core functionality from the `AutonomousAgent` and can be used as a drop in replacement for any functions the query the agent directly for data.
The `PlaybackAgent` also includes control functions to set the currently active frame from the data set, `set_frame()`, and to step to the next frame `step_frame()`.
`input_data()` will provide an `input_data` dictionary normally provided by the simulator to the `run_step()` method of the `AutonomousAgent`.

```python
# Create a playback agent
agent = PlaybackAgent("examples/example.lac")

frame = 1
done = False
while not done:

    # Get some data from the agent
    imu_data = agent.get_imu_data()

    # Do something with the data
    print(f"Frame {frame}: {imu_data}")

    # Get input data from the cameras
    input_data = agent.input_data()

    # Check if we reached the end of the recording
    done = agent.at_end()

    # Step the agent to the next frame
    frame = agent.step_frame()

# Jump to a specific frame
agent.set_frame(120)

# Get camera specific data:
print(f"BackLeft Camera Enabled? {agent.get_camera_state('BackLeft')}")
```
