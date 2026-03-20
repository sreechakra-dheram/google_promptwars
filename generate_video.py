import cv2
import numpy as np

# Create a 3-second 1fps video
out = cv2.VideoWriter('dummy_cctv.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 1, (640, 480))

for i in range(3):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    if i == 0:
        cv2.putText(frame, "Pre-impact", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    elif i == 1:
        cv2.putText(frame, "Impact", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        # Add red flash
        frame[:, :] = [0, 0, 255]
        cv2.putText(frame, "Impact", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    else:
        cv2.putText(frame, "Aftermath", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3)
    out.write(frame)

out.release()
