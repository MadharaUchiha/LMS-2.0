# Import the necessary libraries
import cv2
from pyzbar.pyzbar import decode
import time

def scan_codes():
    """
    Opens the webcam and scans for barcodes and QR codes,
    printing the decoded data to the console.
    """
    # Initialize the video capture object
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    print("Scanner started. Point a barcode or QR code at the camera. Press 'q' to quit.")

    while True:
        # Read a frame from the video stream
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        # Decode all barcodes and QR codes in the frame
        decoded_objects = decode(frame)

        # Loop through each detected code
        for obj in decoded_objects:
            # Print the decoded data and the type of code
            decoded_data = obj.data.decode('utf-8')
            code_type = obj.type
            print(f"[{time.strftime('%H:%M:%S')}] Detected {code_type}: {decoded_data}")

            # Draw a bounding box around the detected code
            points = obj.polygon
            if len(points) > 4:
                # For complex shapes, a convex hull is more reliable
                hull = cv2.convexHull(
                    cv2.UMat(points), returnPoints=True
                )
                cv2.polylines(frame, [hull], True, (0, 255, 0), 2)
            else:
                cv2.polylines(frame, [points], True, (0, 255, 0), 2)
            
            # Put the decoded data on the image for real-time feedback
            cv2.putText(frame, decoded_data, (obj.rect.left, obj.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        # Display the frame with the bounding boxes
        cv2.imshow('Code Scanner', frame)

        # Break the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and destroy all windows
    cap.release()
    cv2.destroyAllWindows()

if _name_ == "_main_":
    scan_codes()