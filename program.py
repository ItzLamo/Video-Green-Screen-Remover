import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import os

# Global variables
video_path = None
background_path = None
lower_green = np.array([35, 50, 50])  # Default green screen range
upper_green = np.array([85, 255, 255])
is_playing = False
current_frame = 0
total_frames = 0
output_path = None
audio_clip = None
background = None

# Function to remove green screen
def remove_green_screen(frame, background, transparency=1.0):
    background = cv2.resize(background, (frame.shape[1], frame.shape[0]))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask_inv = cv2.bitwise_not(mask)
    fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    bg = cv2.bitwise_and(background, background, mask=mask)
    combined = cv2.add(fg, bg)
    return cv2.addWeighted(combined, transparency, background, 1 - transparency, 0)

# Function to handle video upload
def upload_video():
    global video_path, total_frames, current_frame, audio_clip
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov")])
    if file_path:
        video_path = file_path
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        current_frame = 0
        cap.release()

        # Load audio
        try:
            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio
            video_clip.close()
        except Exception as e:
            messagebox.showwarning("Audio Warning", "Could not load audio from video file.")
            audio_clip = None

        status_label.config(text=f"Video loaded: {os.path.basename(file_path)}")
        update_preview()

# Function to handle background upload
def upload_background():
    global background_path, background
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if file_path:
        background_path = file_path
        background = cv2.imread(background_path)
        status_label.config(text=f"Background loaded: {os.path.basename(file_path)}")
        update_preview()

# Function to update preview
def update_preview():
    if video_path is None or background_path is None:
        return

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
    ret, frame = cap.read()
    if not ret:
        return

    # Process frame
    processed = remove_green_screen(frame, background)

    # Resize for preview
    height, width = processed.shape[:2]
    max_size = 400  # Smaller preview size
    if width > max_size or height > max_size:
        ratio = max_size / max(width, height)
        processed = cv2.resize(processed, (int(width * ratio), int(height * ratio)))

    # Convert to PhotoImage
    processed_rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(processed_rgb)
    img_tk = ImageTk.PhotoImage(image=img)

    # Update canvas
    preview_canvas.config(width=img.width, height=img.height)
    preview_canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    preview_canvas.image = img_tk

    cap.release()

# Function to process and save the video
def process_video():
    if video_path is None or background_path is None:
        messagebox.showerror("Error", "Please upload both video and background!")
        return

    status_label.config(text="Processing video...")
    root.update_idletasks()

    # Load video
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Create output video writer
    output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Process each frame
        for i in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break

            processed = remove_green_screen(frame, background)
            out.write(processed)

            # Update progress
            progress = (i + 1) / total_frames * 100
            progress_bar["value"] = progress
            status_label.config(text=f"Processing frame {i + 1}/{total_frames}")
            root.update_idletasks()

        out.release()
        cap.release()

        # Add audio to the output video
        if audio_clip is not None:
            video_clip = VideoFileClip(output_path)
            final_clip = video_clip.with_audio(audio_clip)  # Use set_audio instead of with_audio
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            video_clip.close()
            audio_clip.close()

        status_label.config(text=f"Video saved to {output_path}")
        progress_bar["value"] = 0  # Reset progress bar

# Create the main window
root = tk.Tk()
root.title("Video Green Screen Remover")
root.geometry("1000x700")

# Use ttk for themed widgets
style = ttk.Style()
style.configure("TButton", padding=5, font=("Helvetica", 10))
style.configure("TLabel", font=("Helvetica", 10))

# Title
title_label = ttk.Label(root, text="Video Green Screen Remover", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

# Video upload section
video_frame = ttk.Frame(root)
video_frame.pack(pady=10)

ttk.Label(video_frame, text="Video:").grid(row=0, column=0, padx=10)
ttk.Button(video_frame, text="Upload Video", command=upload_video).grid(row=0, column=1, padx=10)

# Background upload section
background_frame = ttk.Frame(root)
background_frame.pack(pady=10)

ttk.Label(background_frame, text="Background:").grid(row=0, column=0, padx=10)
ttk.Button(background_frame, text="Upload Picture", command=upload_background).grid(row=0, column=1, padx=10)

# Preview canvas
preview_canvas = tk.Canvas(root, width=400, height=300, bg="black")
preview_canvas.pack(pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=800, mode="determinate")
progress_bar.pack(pady=10)

# Process button
process_button = ttk.Button(root, text="Process and Save", command=process_video)
process_button.pack(pady=10)

# Status bar
status_label = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

# Run the application
root.mainloop()