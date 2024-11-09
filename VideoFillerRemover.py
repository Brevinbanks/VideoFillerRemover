"""
    ****************************************************
    *                                                  *
    *               VIDEO FILLER REMOVER               *
    *                                                  *
    *    Script Created By: Brevin                     *
    *    Date: November 8, 2024                        *
    *    License: MIT                                  *
    *                                                  *
    *    Description:                                  *
    *    This script processes vlog-style videos,      *
    *    automatically removing silence and filler     *
    *    words such as 'um'.                           *
    *                                                  *
    *    GitHub: https://github.com/YourGithub         *
    *    YouTube: https://youtube.com/YourChannel      *
    *    Website: https://yourwebsite.com              *
    *                                                  *
    ****************************************************
"""

import os
import tkinter as tk # GUI tools
from tkinter import filedialog, messagebox # GUI log tools
from tkinter import ttk # GUI tools
from moviepy.editor import VideoFileClip # Tools for cutting and editing video files
from moviepy.editor import concatenate_videoclips # Tools for cutting and editing video files
import moviepy.config as mpc
import whisper # AI API to detect silence and filler words like um
import threading 
import time 
import traceback # Use to send command window and log outputs to the GUI window
from pydub import AudioSegment # Tools for separating audio segments
from pydub.silence import detect_silence # For detecting silience in an audio segment
from PIL import Image, ImageTk  # For frame preview and icons
import winsound  # For sound notifications (Windows only)
import sys
import webbrowser





# Point to where you have extracted ffmpeg - make sure this is relative to the script's location
script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the script's directory
ffmpeg_path = os.path.join(script_dir, "ffmpeg-master-latest-win64-gpl", "bin", "ffmpeg.exe")
print(f"FFMPEG_BINARY path: {ffmpeg_path}")  # Debugging line
os.environ["FFMPEG_BINARY"] = ffmpeg_path

# Set FFMPEG path for moviepy
mpc.FFMPEG_BINARY = ffmpeg_path

# Redirect standard output to the embedded terminal
class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)

    def flush(self):
        pass


class VideoFillterGUI():
    def __init__(self):

        # Create the main Tkinter window
        self.root = tk.Tk()

        # Set the window title
        self.root.title("Brevengineering Video Filler And Silence Remover")

        # Correctly resolve the path to the bundled file
        if getattr(sys, 'frozen', False):
            # If running from a packaged executable
            base_path = sys._MEIPASS  # Path to the temporary folder where files are extracted
        else:
            # If running from the script directly
            base_path = os.path.dirname(os.path.abspath(__file__))

        azure_tcl_path = os.path.join(base_path, 'azure.tcl')

        # Apply a modern dark theme using an external theme file 'azure.tcl'
        self.root.tk.call("source", azure_tcl_path)
        self.root.tk.call("set_theme", "dark")
     
        # Boolean variable to track whether sound is enabled (True by default)
        self.sound_enabled = tk.BooleanVar(value=True)

        # Create and position a label and entry box for selecting the video file
        tk.Label(self.root, text="Select Video File").grid(row=0, column=0, padx=10, pady=30)
        self.video_file_entry = ttk.Entry(self.root, width=50)
        self.video_file_entry.grid(row=0, column=1)

        # Button to browse and select the video file
        ttk.Button(self.root, text="Browse", command=self.browse_file).grid(row=0, column=2, padx = 10, pady=10)

        # Create and position a label and entry box for selecting the output folder
        tk.Label(self.root, text="Select Output Folder").grid(row=1, column=0, padx=10, pady=10)
        self.output_folder_entry = ttk.Entry(self.root, width=50)
        self.output_folder_entry.grid(row=1, column=1)

        # Button to browse and select the output folder
        ttk.Button(self.root, text="Browse", command=self.browse_output_folder).grid(row=1, column=2, padx = 10, pady=10)

        # Create and position a label and entry box for entering the output file name
        tk.Label(self.root, text="Output File Name").grid(row=2, column=0, padx=10, pady=10)
        self.output_name_entry = ttk.Entry(self.root, width=50)
        self.output_name_entry.grid(row=2, column=1)

        # Button to start the video processing operation
        ttk.Button(self.root, text="Start", command=self.start_processing).grid(row=3, column=1, pady=10)

        # Create a progress bar to show processing progress
        self.progress_bar = ttk.Progressbar(self.root, length=400, mode="determinate")
        self.progress_bar.grid(row=4, column=1, padx=10)

        # Label to display the percentage of progress
        self.percentage_label = tk.Label(self.root, text="0%")
        self.percentage_label.grid(row=4, column=2)

        # Label to show the status of processing
        self.status_label = tk.Label(self.root, text="Progress will be displayed here")
        self.status_label.grid(row=5, column=1, pady=10)

        # Preview label to display video frames (if needed)
        self.preview_label = ttk.Label(self.root)
        self.preview_label.grid(row=5, rowspan = 5, column=3, columnspan=3, pady=10, padx=10)

        # Mute button to toggle sound settings (default is ON)
        self.mute_button = ttk.Button(self.root, text="Play Sound When Finished: ON", command=self.toggle_sound)
        self.mute_button.grid(row=3, column=0, pady=10, padx=10)

        # Load and set the window icon
        self.icon = Image.open("BrevengineeringIcon.jpg")  # Replace with your icon file path
        self.icon = ImageTk.PhotoImage(self.icon)
        self.root.iconphoto(True, self.icon)  # Set the icon for the window

        # Slider for sound quietness threshold (-21 dB default)
        self.quiet_threshold_label = ttk.Label(self.root, text="Sound Quietness Threshold (dBFs):")
        self.quiet_threshold_label.grid(row=5, column=0, pady=10, padx=10)
        self.quiet_threshold_slider = ttk.Scale(self.root, from_=-60, to=0, value=-21, orient=tk.HORIZONTAL)
        self.quiet_threshold_slider.grid(row=6, column=0, pady=10, padx=10)
        self.quiet_threshold_value = ttk.Label(self.root, text=f"Current: {-21} dBFs")
        self.quiet_threshold_value.grid(row=6, column=1, pady=10, padx=10)

        # Slider for cut padding time (-0.2s default)
        self.cut_padding_label = ttk.Label(self.root, text="Cut Padding Time (s):")
        self.cut_padding_label.grid(row=7, column=0, pady=10, padx=10)
        self.cut_padding_slider = ttk.Scale(self.root, from_=-1, to=0, value=-0.2, orient=tk.HORIZONTAL)
        self.cut_padding_slider.grid(row=8, column=0, pady=10, padx=10)
        self.cut_padding_value = ttk.Label(self.root, text=f"Current: {-0.2} s")
        self.cut_padding_value.grid(row=8, column=1, pady=10, padx=10)

        # Slider for minimum silence length (650ms default)
        self.min_silence_label = ttk.Label(self.root, text="Minimum Silence Length (ms):")
        self.min_silence_label.grid(row=9, column=0, pady=10, padx=10)
        self.min_silence_slider = ttk.Scale(self.root, from_=0, to=2000, value=650, orient=tk.HORIZONTAL)
        self.min_silence_slider.grid(row=10, column=0, pady=10, padx=10)
        self.min_silence_value = ttk.Label(self.root, text=f"Current: 650 ms")
        self.min_silence_value.grid(row=10, column=1, pady=10, padx=10)

        # Update displayed values when sliders are adjusted
        self.quiet_threshold_slider.bind("<Motion>", self.update_threshold_label)
        self.cut_padding_slider.bind("<Motion>", self.update_padding_label)
        self.min_silence_slider.bind("<Motion>", self.update_silence_label)


        # Text box to display terminal output or logs
        self.terminal_output = tk.Text(self.root, height=10, width=60)
        self.terminal_output.grid(row=0, rowspan = 3, column=4, padx = 5, pady=10)


        # YouTube Channel: https://www.youtube.com/@Brevengineering
        # GitHub: https://github.com/Brevinbanks
        # Personal Website: https://brevinbanks.github.io/

        # Create labels with hyperlinks
        youtube_label = tk.Label(self.root, text="YouTube Channel", fg="#006D6F", cursor="hand2")
        youtube_label.grid(row=11, column=0, padx = 5, pady=3)
        youtube_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.youtube.com/@Brevengineering"))

        github_label = tk.Label(self.root, text="GitHub", fg="#006D6F", cursor="hand2")
        github_label.grid(row=11, column=1, padx = 5, pady=3)
        github_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/Brevinbanks"))

        website_label = tk.Label(self.root, text="Personal Website", fg="#006D6F", cursor="hand2")
        website_label.grid(row=11, column=2,  padx = 5, pady=3)
        website_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://brevinbanks.github.io/"))

        # Redirect the standard output to the Text box
        sys.stdout = TextRedirector(self.terminal_output)

        # Start the Tkinter event loop
        self.root.mainloop()

    def update_threshold_label(self, event=None):
        # Update quietness threshold label
        current_value = self.quiet_threshold_slider.get()
        self.quiet_threshold_value.config(text=f"Current: {current_value:.1f} dBFs")

    def update_padding_label(self, event=None):
        # Update cut padding time label
        current_value = self.cut_padding_slider.get()
        self.cut_padding_value.config(text=f"Current: {current_value:.2f} s")

    def update_silence_label(self, event=None):
        # Update minimum silence length label
        current_value = self.min_silence_slider.get()
        self.min_silence_value.config(text=f"Current: {int(current_value)} ms")

    def browse_file(self):
        # Open a file dialog to select a video file (specifically .mp4 files)
        video_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("MP4 files", "*.mp4")])
        
        # If a valid file path is selected
        if video_path:
            # Clear the current text in the video file entry field
            self.video_file_entry.delete(0, tk.END)
            
            # Insert the selected file path into the video file entry field
            self.video_file_entry.insert(0, video_path)

    def browse_output_folder(self):
        # Open a directory dialog to select the output folder
        output_path = filedialog.askdirectory(title="Select Output Folder")
        
        # If a valid folder path is selected
        if output_path:
            # Clear the current text in the output folder entry field
            self.output_folder_entry.delete(0, tk.END)
            
            # Insert the selected folder path into the output folder entry field
            self.output_folder_entry.insert(0, output_path)

    def preview_frame(self, image_frame):
        """ Update the preview image in the GUI with the current frame """
        
        # Convert the OpenCV frame (numpy array) to a PIL image
        frame = Image.fromarray(image_frame)
        
        # Resize the image to fit within the GUI (240x135 pixels)
        frame = frame.resize((240, 135))
        
        # Convert the PIL image to an ImageTk format for Tkinter
        img = ImageTk.PhotoImage(frame)
        
        # Update the image in the preview label
        self.preview_label.config(image=img)
        
        # Store a reference to the image to prevent garbage collection
        self.preview_label.image = img

    def toggle_sound(self):
        """ Toggle the sound on/off state and update the button text accordingly """
        
        # If sound is currently enabled
        if self.sound_enabled.get():
            # Disable sound
            self.sound_enabled.set(False)
            
            # Update the button text to indicate sound is OFF
            self.mute_button.config(text="Play Sound When Finished: OFF")
        
        # If sound is currently disabled
        else:
            # Enable sound
            self.sound_enabled.set(True)
            
            # Update the button text to indicate sound is ON
            self.mute_button.config(text="Play Sound When Finished: ON")


    def start_processing(self):
        # Get the file path from the video file entry field
        video_file = self.video_file_entry.get()
        
        # Get the folder path from the output folder entry field
        output_folder = self.output_folder_entry.get()
        
        # Get the desired output file name from the output name entry field
        output_file = self.output_name_entry.get()

        # If any of the fields are empty, show an error message and stop processing
        if not video_file or not output_folder or not output_file:
            messagebox.showerror("Error", "Please select video file, output folder, and output file name.")
            return

        # Construct the full output path for the processed video file
        output_path = os.path.join(output_folder, f"{output_file}.mp4")
        
        # Reset the progress bar to 0 and update the status label to indicate the start of the process
        self.progress_bar['value'] = 0
        self.status_label.config(text="Starting...")
        
        # Ensure that the Tkinter interface is updated before starting the processing
        self.root.update_idletasks()

        # Define a callback function to update the progress bar, status, and percentage label
        def progress_callback(status, percent):
            # Update the progress bar with the current percentage
            self.progress_bar['value'] = percent
            
            # Update the status label with the current status message
            self.status_label.config(text=status)
            
            # Update the percentage label with the current progress percentage
            self.percentage_label.config(text=f"{percent}%")
            
            # Ensure the GUI updates during processing
            self.root.update_idletasks()

        # Define a function that runs the video processing in a separate thread
        def process_thread():
            # Call the method to process the video file
            # Pass in the video file, output path, the progress callback, the frame preview function, and sound enabled state
            success = self.process_video(video_file, output_path, progress_callback, self.preview_frame, self.sound_enabled.get())
            
            # If the video processing is successful, update the status label accordingly
            if success:
                self.status_label.config(text="Process completed successfully!")
            # If the video processing fails, update the status label to indicate failure
            else:
                self.status_label.config(text="Process failed!")

        # Start the video processing in a new thread to prevent freezing the GUI during processing
        threading.Thread(target=process_thread).start()


    # Detect silence in audio file
    def detect_silences(self, audio_file):
        audio = AudioSegment.from_wav(audio_file)
        silent_intervals = detect_silence(
            audio,
            min_silence_len=self.min_silence_slider.get(),  # Require 1 second of silence
            silence_thresh=audio.dBFS + self.quiet_threshold_slider.get(),
            seek_step=1
        )
        silent_intervals = [(start / 1000, end / 1000) for start, end in silent_intervals]
        return silent_intervals

    # Process the video
    def process_video(self, video_file, output_file, progress_callback, preview_callback, play_sound):
        # Record the start time of the video processing
        start_time = time.time()
        
        try:
            # Step 1: Loading the video file
            progress_callback("Loading video...", 10)
            video_clip = VideoFileClip(video_file)  # Load the video file using MoviePy
            
            # Step 2: Extracting the audio from the video
            progress_callback("Extracting audio from video...", 20)
            audio_file = "temp_audio.wav"  # Temporary file to store extracted audio
            video_clip.audio.write_audiofile(audio_file, codec="pcm_s16le")  # Save the audio in WAV format
            
            # Step 3: Detecting silent intervals in the audio
            progress_callback("Detecting silences...", 40)
            silent_intervals = self.detect_silences(audio_file)  # Custom function to detect silent parts
            
            # Step 4: Using the Whisper model to detect filler words in the audio
            progress_callback("Detecting filler words...", 60)
            model = whisper.load_model("base")  # Load the Whisper speech recognition model
            result = model.transcribe(audio_file)  # Transcribe the audio using Whisper
            
            filler_intervals = []  # List to store intervals where filler words are detected
            segments = result['segments']  # Extract speech segments from the transcription
            padding = self.cut_padding_slider.get()  # Add a 200ms padding before and after each filler word

            # Loop through the segments to detect filler words (e.g., "um")
            for segment in segments:
                if 'words' in segment:
                    for word_data in segment['words']:
                        word = word_data.get('text', '').lower()  # Get the word in lowercase
                        if word == "um":  # If the word is "um"
                            start = max(0, word_data['start'] + padding)  # Calculate start time with padding
                            end = min(video_clip.duration, word_data['end'] - padding)  # Calculate end time with padding
                            filler_intervals.append((start, end))  # Add the filler word interval to the list

            # Step 5: Merging silent intervals and filler word intervals for cutting
            progress_callback("Cutting intervals...", 80)
            intervals_to_cut = silent_intervals + filler_intervals  # Combine silences and filler word intervals
            intervals_to_cut.sort(key=lambda x: x[0])  # Sort the intervals by start time

            subclips = []  # List to store subclips of video that will be kept
            last_end = 0  # Track the end of the last subclip
            
            # Loop through the intervals to cut and create subclips
            for start, end in intervals_to_cut:
                start_with_padding = max(last_end, start - padding)  # Adjust start time with padding
                end_with_padding = min(end + padding, video_clip.duration)  # Adjust end time with padding

                # If the current interval is valid, add the subclip to the list
                if start_with_padding > last_end:
                    subclips.append(video_clip.subclip(last_end, start_with_padding))  # Create subclip from last_end to start_with_padding
                
                last_end = end_with_padding  # Update the end of the last subclip

                # Show a preview frame (approximation) in the GUI
                frame_time = (start_with_padding + end_with_padding) / 2  # Calculate midpoint of the interval
                preview_callback(video_clip.get_frame(frame_time))  # Display the frame in the preview area

            # If there is any remaining part of the video after the last interval, add it as a subclip
            if last_end < video_clip.duration:
                subclips.append(video_clip.subclip(last_end, video_clip.duration))  # Append the remaining part of the video
            
            # Step 6: Concatenating all the subclips into the final video
            final_clip = concatenate_videoclips(subclips)  # Concatenate subclips to form the final video
            progress_callback("Saving video...", 90)
            final_clip.write_videofile(output_file, codec="libx264")  # Save the final video to the specified output file
            
            # Step 7: Final status and completion message
            progress_callback("Completed!", 100)
            elapsed_time = time.time() - start_time  # Calculate total elapsed time
            print(f"Process completed in {elapsed_time:.2f} seconds.")  # Print the time taken for processing
            
            # Step 8: Play a sound when processing is complete if sound is enabled
            if play_sound:
                winsound.Beep(1000, 500)  # Play a beep sound (1000 Hz for 500ms) as notification

            return True  # Return True to indicate successful processing
        
        # Handle any exceptions that occur during video processing
        except Exception as e:
            # Update progress bar and status message to indicate error
            progress_callback(f"Error: {str(e)}", 0)
            elapsed_time = time.time() - start_time  # Calculate elapsed time before error
            print(f"Error after {elapsed_time:.2f} seconds: {e}")  # Print error and time taken before failure
            traceback.print_exc()  # Print the full traceback of the exception for debugging
            return False  # Return False to indicate failure


if __name__ == "__main__":
    filter_app = VideoFillterGUI() # Create the filter application
