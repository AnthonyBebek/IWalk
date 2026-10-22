import stream
import motorcontroller
import asyncio
from parameters import MOTOR_1, MOTOR_2

async def main():
    # open connection

    client_socket, cap = stream.connect()

    try:
        while True:
            hazard_status = stream.capture_and_stream_a_single_frame(cap, client_socket)
            if hazard_status == 0:
                #print("No hazards detected.")
                pass
            elif hazard_status == 1:
                print("Left hazard detected!")
                await motorcontroller.shake_motor(MOTOR_1, duration_seconds=3.0, intensity_steps=100)
            elif hazard_status == 2:
                print("Right hazard detected!")
                await motorcontroller.shake_motor(MOTOR_2, duration_seconds=3.0, intensity_steps=100)
            elif hazard_status == 3:
                print("Hazards detected on both sides!")
                await motorcontroller.shake_motor(MOTOR_1, duration_seconds=3.0, intensity_steps=100)
                await motorcontroller.shake_motor(MOTOR_2, duration_seconds=3.0, intensity_steps=100)
            elif hazard_status == 4:
                print("Error: Could not capture or send frame.")

    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")
        await stream.close_connections(cap, client_socket)

if __name__ == '__main__':
    asyncio.run(motorcontroller.setup())  # Ensure motors are set up before starting the main loop
    asyncio.run(main())
