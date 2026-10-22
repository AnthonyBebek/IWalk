import cv2
import socket
import struct

RECEIVER_IP = '192.168.30.84'
PORT = 6767



def connect():
    # Connect to the remote server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to {RECEIVER_IP}:{PORT}...")
    client_socket.connect((RECEIVER_IP, PORT))
    print("Connected! Streaming video and awaiting alerts... (Press Ctrl+C to stop)\n")
    
    cap = cv2.VideoCapture(0)
    return client_socket, cap
        

def capture_and_stream_a_single_frame(cap, client_socket) -> int:
    '''
    Capture a single frame from the webcam and stream it to the server.

    Returns:
        int: 0 - 4 signifying either no hazards, left hazard, right hazard, both sides or an error.
    '''

    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame from webcam.")
        return 4

    # 1. Compress frame as JPEG
    ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    data = buffer.tobytes()
    message = struct.pack("Q", len(data)) + data
    
    # 2. Send frame to server
    client_socket.sendall(message)

    # 3. Receive 2 booleans back from server (2 bytes)
    response = client_socket.recv(2)
    if not response or len(response) < 2:
        print("Server disconnected.")
        return 4

    left_alert, right_alert = struct.unpack("??", response)

    # 4. Print status directly to the terminal
    if left_alert and right_alert:
        return 3
    elif left_alert:
        return 1
    elif right_alert:
        return 2
    else:
        return 0



def close_connections(cap, client_socket):
    cap.release()
    client_socket.close()


def main():
    pass

if __name__ == '__main__':
    main()
