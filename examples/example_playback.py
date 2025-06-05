from lunarloc import PlaybackAgent

if __name__ == "__main__":
    agent = PlaybackAgent("examples/example.lac")

    print("Starting playback...")

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
