# Video Filler Remover

This project is a Python-based tool that processes vlog-style videos, automatically removing silence and filler words like "um" for a cleaner, more professional edit.

## Features
- **Detects filler words**: Uses the Whisper AI API to detect and remove filler words.
- **Removes silence**: Cuts out long periods of silence from video files.
- **GUI**: A Tkinter-based graphical interface for easy file selection and control.


If you'd prefer just an out of the box EXE file you can download and run 'Video Filler Remover.exe'
This should work with windows, but if you run into problems they may be fixed as long as you follow the ffmpeg steps below in number 4 by nstalling ffmpeg through choco [(choclatey)](https://chocolatey.org/install)

## Installation

### Prerequisites
Ensure you have Python 3.x installed. You'll also need the following libraries:

- os
- tkinter
- moviepy
- whisper
- threading
- pydub
- PIL
- winsound
- webbrowser

### Virtual Environment Setup
1. Clone the repository or download the files.
2. In the project root directory, create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate the virtual environment (on Windows)
.\venv\Scripts\activate

# Activate the virtual environment (on Mac/Linux)
source venv/bin/activate

```
3. Install dependencies
```bash

pip install -r requirements.txt

```
4. Check if your computer requires ffmpeg from ffmpeg.org. It could be a missing dependency often needed for whisper or moviepyy

Some libraries like whisper depend on certain system libraries (like ffmpeg for video processing). Make sure you have those dependencies installed. You can install ffmpeg using:
These binaries are included (Windows 10+ compatible versions only) in this repository (ffmpeg-master-latest-win64) - but they may not work for all users and machines. Either way you must still add ffmpeg to your PATH Environment if not already done (see below).

-Windows: Download from [ffmpeg.org](https://www.ffmpeg.org/download.html). Extract the windows binary. There are 2 different 3rd party compilations available - i found [BtbN's](https://github.com/BtbN/FFmpeg-Builds/releases)  ffmpeg-master-latest-win64-gpl.zip to work for me. You'll need to extract the folder to get the executable, then you'll need to edit your PATH environment to include this exe.
- If you'd prefer the command line version for windows, run the command window as an administrator with the following command:
```bash
choco install ffmpeg
```
Type Y when it prompts inorder to add it to your PATH environment.


-Linux/macOS: Install using apt-get or brew. Similar to the windows method after downloading the linux or mac binaries.


### Usage

    Run the Video Filler Remover Script:

```bash
python VideoFillerRemover.py

```
A GUI window will open where you can select the video file, choose an output folder, and start processing the video.
You can also name the output file.
There are 3 sliders to help tune the way the script cuts.
- The sound quietness threshold determines how quiet the video section must be to be detected as a quiet interval
- The cut padding time says how much time to delay cutting the video after detecting the start of a silence interval. The padding also determines how much time to retract from the end of the silence interval. This helps to prevent quick jumps between words that may make things sound too fast or jumbled.
- The minimum silence length determines how long a silent interval must at least be before the script does any cutting from that section.

The default values for the above settings are -21 dBFs, -0.2s, and 650ms respectively. This is what worked for me in a medium-sized room alone.
It should be tuned accordingly for your recording conditions.

When you are ready to trim the video, press the start button.

Periodic notifications will be shown in the top right notification window. These will let you know when the video editing begins the next step.

It may take a lot of time depending on the video size and format. The terminal window will display the current frames of the video being edited and let you know the progress.

If the video has successfully found clips to cut you will see a preview of the current frames in the editing process in the bottom right.

When the video is finished editing, a sound will play. This can be disabled if you like.


You may notice there will be a left of temp_audo.wav file after it finishes a video. It uses this to separate the audio from the video and then restor them. After you have finished the clipping you can delete this file.

## Customization Note

This project uses the `azure.tcl` library from [Azure-ttk-theme](https://github.com/rdbende/Azure-ttk-theme). However, I have modified the default color scheme by replacing the blue color with a custom teal shade that aligns with my personal branding. The new color reflects the **Brevengineering** logo, providing a unique and customized theme for the application.

Please be aware that while the core functionality and style are based on the `azure.tcl` library, the color change may not be compatible with all existing designs that rely on the default color palette. Adjustments may be necessary if you plan to use this theme with other styles or branding.


### License

This project is licensed under the MIT License. See the LICENSE file for more information.

### Author

**Brevin Banks:**
        - [YouTube Channel](https://www.youtube.com/@Brevengineering)
        - [GitHub](https://github.com/Brevinbanks)
        - [Personal Website](https://brevinbanks.github.io/)

```bash
