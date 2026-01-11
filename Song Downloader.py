from ast import arg
import os
from pathlib import Path
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import sys

#subprocess.run(["pip3", "install", "yt-dlp"]) 

import yt_dlp

def download_youtube_as_wav(url, output_filename="audio", track_title=None, status_callback=None):
    """
    Downloads a YouTube video's audio as a WAV file with custom metadata.
    Uses FFmpeg directly instead of pydub for Python 3.13+ compatibility.
    
    Args:
        url: YouTube video URL
        output_filename: Desired output filename (without extension)
        track_title: Custom track title for metadata (optional)
        status_callback: Function to call with status updates
    
    Returns:
        Path to the final WAV file
    """

    output_dir = str(Path.home()) + "/Desktop/Downloaded Songs/"
    os.makedirs(output_dir, exist_ok=True)
    final_wav = f"{output_dir}{output_filename}.wav"

    # If no track title provided, use the filename
    if track_title is None:
        track_title = output_filename
    
    # Configure yt-dlp to download and convert directly to WAV
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}{output_filename}',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        },
        {
            'key': 'FFmpegMetadata',
            'add_metadata': False,  # Don't add YouTube metadata
        }],
        'postprocessor_args': [
            '-ar', '44100',  # Sample rate
            '-ac', '2',       # Stereo
            '-map_metadata', '-1',  # Remove all existing metadata
            '-metadata', f'title={track_title}',  # Add ONLY custom title
            '-fflags', '+bitexact',  # Remove encoding metadata
        ],
        # Add these to avoid 403 errors
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'cookiesfrombrowser': ('chrome',),  # Use Chrome cookies if available
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        if status_callback:
            status_callback(f"Downloading audio from: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if status_callback:
            status_callback(f"✓ Successfully created: {final_wav}")
        
        return final_wav
        
    except Exception as e:
        if status_callback:
            status_callback(f"Error: {e}")
        return None


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    # Common FFmpeg installation paths
    common_paths = [
        '/usr/local/bin/ffmpeg',
        '/opt/homebrew/bin/ffmpeg',
        '/opt/local/bin/ffmpeg',
        '/usr/bin/ffmpeg',
    ]
    
    # First try system PATH
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, 
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try common installation paths
    for path in common_paths:
        if os.path.exists(path):
            try:
                subprocess.run([path, '-version'], 
                              capture_output=True, 
                              check=True)
                # Set the path for yt-dlp to use
                os.environ['PATH'] = os.path.dirname(path) + ':' + os.environ.get('PATH', '')
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
    
    return False

def create_gui():
    """Create and run the GUI"""
    # Create main window
    root = tk.Tk()
    root.title("YouTube to WAV Downloader")
    root.geometry("450x280")
    root.resizable(False, False)

    # Main container
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    # Label + Entry 1
    label1 = ttk.Label(frame, text="YouTube URL:")
    label1.pack(anchor="w", pady=(0, 4))

    entry1 = ttk.Entry(frame, width=50)
    entry1.pack(fill="x", pady=(0, 12))
    entry1.focus()  # initial keyboard focus

    # Label + Entry 2
    label2 = ttk.Label(frame, text="Track Title:")
    label2.pack(anchor="w", pady=(0, 4))

    entry2 = ttk.Entry(frame, width=50)
    entry2.pack(fill="x", pady=(0, 16))

    # Status label
    status_label = ttk.Label(frame, text="Ready", wraplength=400)
    status_label.pack(fill="x", pady=(0, 12))

    def update_status(message):
        status_label.config(text=message)
        root.update_idletasks()

    def on_submit(event=None):
        url = entry1.get().strip()
        title = entry2.get().strip()
        
        if not url:
            messagebox.showwarning("Input Required", "Please enter a YouTube URL")
            return
        
        if not title:
            messagebox.showwarning("Input Required", "Please enter a track title")
            return
        
        # Disable button during download
        submit_btn.config(state="disabled")
        update_status("Downloading... Please wait.")
        
        try:
            # Download and convert with custom metadata
            output_file = download_youtube_as_wav(url, title, title, update_status)
            
            if output_file:
                messagebox.showinfo("Success", f"File saved:\n{output_file}\n\nTrack title: {title}")
                update_status("Download complete!")
                # Clear entries after successful download
                entry1.delete(0, tk.END)
                entry2.delete(0, tk.END)
                entry1.focus()
            else:
                messagebox.showerror("Error", "Download failed. Please check the URL and try again.")
                update_status("Download failed")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            update_status(f"Error: {str(e)}")
        finally:
            # Re-enable button
            submit_btn.config(state="normal")

    # Submit button
    submit_btn = ttk.Button(frame, text="Download", command=on_submit)
    submit_btn.pack(fill="x")

    # Keyboard bindings
    root.bind("<Return>", on_submit)

    root.mainloop()

if __name__ == "__main__":
    try:
        # Check for FFmpeg first
        if not check_ffmpeg():
            # Show error in GUI if possible
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showerror(
                "FFmpeg Not Found",
                "FFmpeg is not installed!\n\n"
                "Please install FFmpeg:\n"
                "  Mac: brew install ffmpeg\n"
                "  Linux: sudo apt install ffmpeg\n"
                "  Windows: Download from ffmpeg.org"
            )
            sys.exit(1)
        
        # Run the GUI
        create_gui()
        
    except Exception as e:
        # Emergency error handler for any uncaught exceptions
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Application Error", f"An error occurred:\n\n{str(e)}")
        except:
            # If even that fails, write to a log file
            log_path = str(Path.home()) + "/Desktop/song_downloader_error.log"
            with open(log_path, "w") as f:
                f.write(f"Error: {str(e)}\n")
                import traceback
                traceback.print_exc(file=f)