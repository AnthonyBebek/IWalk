import time
import sys
from dynamixel_sdk import *
from parameters import *
import asyncio

# Initialize Handlers
portHandler = PortHandler(DEVICE_NAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

async def shake_motor(motor_id, duration_seconds=1.0, intensity_steps=40, speed_setting=0):
    current_pos, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, motor_id, ADDR_MX_PRESENT_POSITION)
    if dxl_comm_result != COMM_SUCCESS:
        print("Failed to read baseline position for shaking. Aborting shake.")
        return
    packetHandler.write2ByteTxRx(portHandler, motor_id, ADDR_MX_MOVING_SPEED, speed_setting)

    print("current position:", current_pos)

    left_target = max(0, current_pos - (intensity_steps // 2))
    right_target = min(4095, current_pos + (intensity_steps // 2))

    end_time = time.time() + duration_seconds
    toggle = True

    while time.time() < end_time:
        target = left_target if toggle else right_target 
        packetHandler.write2ByteTxOnly(portHandler, motor_id, ADDR_MX_GOAL_POSITION, target)
        await asyncio.sleep(0.1)  # Adjust the sleep interval for better responsiveness
        toggle = not toggle

async def set_torque(state):
    res1, err1 = packetHandler.write1ByteTxRx(portHandler, MOTOR_1, 24, state)
    res2, err2 = packetHandler.write1ByteTxRx(portHandler, MOTOR_2, 24, state)
    print(f"Torque Enable Status - Motor 1 Err: {err1}, Motor 2 Err: {err2}")
    print(f"Torque Enable Result - Motor 1 Res: {res1}, Motor 2 Res: {res2}")


async def stop_shaking(motor_id):
    if motor_id == MOTOR_1:
        # Logic to stop shaking of Motor 1
        pass
    elif motor_id == MOTOR_2:
        # Logic to stop shaking of Motor 2
        pass

async def main():
    try:
        await set_torque(TORQUE_ENABLE)
        await asyncio.sleep(0.2)
        
        await shake_motor(MOTOR_1, duration_seconds=3.0, intensity_steps=100)
        await shake_motor(MOTOR_2, duration_seconds=3.0, intensity_steps=100)

    except KeyboardInterrupt:
        print("\nStopped early via terminal command.")

    finally:
        print("\nShutting down safely...")
        await set_torque(TORQUE_DISABLE)
        portHandler.closePort()

async def setup():
    """
    Initializes the motor controller, ensures joint mode,
    sets a safe speed, and centers the motors.
    """
    if not portHandler.openPort() or not portHandler.setBaudRate(BAUDRATE):
        print("Serial initialization failed.")
        sys.exit()

    print(f"Connected to COM10.")

    # 1. Enable Torque
    await set_torque(TORQUE_ENABLE)
    await asyncio.sleep(0.2)

    # 2. Force Joint Mode (Ensure they aren't stuck in Wheel Mode)
    # CW Limit = 0 (Address 6), CCW Limit = 4095 (Address 8)
    packetHandler.write2ByteTxRx(portHandler, MOTOR_1, 6, 0)
    packetHandler.write2ByteTxRx(portHandler, MOTOR_1, 8, 4095)
    packetHandler.write2ByteTxRx(portHandler, MOTOR_2, 6, 0)
    packetHandler.write2ByteTxRx(portHandler, MOTOR_2, 8, 4095)
    await asyncio.sleep(0.1)

    # 3. Explicitly set a moving speed (Ensure it's not set to 0 velocity)
    # 200 is a safe, moderate speed out of 1023 max
    packetHandler.write2ByteTxRx(portHandler, MOTOR_1, ADDR_MX_MOVING_SPEED, 200)
    packetHandler.write2ByteTxRx(portHandler, MOTOR_2, ADDR_MX_MOVING_SPEED, 200)
    await asyncio.sleep(0.1)

    # 4. Write Goal Position (Center / 2048)
    dxl_comm_result_1, dxl_error_1 = packetHandler.write2ByteTxRx(portHandler, MOTOR_1, ADDR_MX_GOAL_POSITION, 2048)
    dxl_comm_result_2, dxl_error_2 = packetHandler.write2ByteTxRx(portHandler, MOTOR_2, ADDR_MX_GOAL_POSITION, 2048)

    # Check for errors
    if dxl_error_1 != 0 or dxl_error_2 != 0:
        print(f"Motor 1 Error Pack: {dxl_error_1}, Motor 2 Error Pack: {dxl_error_2}")

    print(dxl_comm_result_1, dxl_comm_result_2)
        
    print("Motor controller setup complete. Torque enabled on both motors.")



if __name__ == '__main__':
    import asyncio
    asyncio.run(setup())
    asyncio.run(main())
