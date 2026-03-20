import cv2
import numpy as np

def extract_frames(video_path: str, num_frames=3):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    
    if total_frames > num_frames:
        frame_indices = [max(int(total_frames*(i/(num_frames-1)))-1, 0) for i in range(num_frames)]
        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
    else:
        while True:
            ret, frame = cap.read()
            if not ret: break
            frames.append(frame)
            if len(frames) == num_frames: break
    cap.release()
    return frames

def encode_image(frame):
    import PIL.Image
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return PIL.Image.fromarray(rgb)

def apply_pii_masking(frame):
    h, w = frame.shape[:2]
    masked = frame.copy()
    
    roi = masked[int(h*0.1):int(h*0.5), int(w*0.3):int(w*0.7)]
    if roi.size > 0:
        masked[int(h*0.1):int(h*0.5), int(w*0.3):int(w*0.7)] = cv2.GaussianBlur(roi, (51, 51), 0)
    
    roi2 = masked[int(h*0.7):h, :]
    if roi2.size > 0:
        masked[int(h*0.7):h, :] = cv2.GaussianBlur(roi2, (51, 51), 0)
        
    return masked
