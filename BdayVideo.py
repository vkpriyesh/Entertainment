#Author : CHETAN RAGHUVANSHI - FOR KRITIKA B'DAY 

from google.colab import files
import shutil
import os
from moviepy.editor import ImageClip, VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip

# === 1. Upload your media ===
# Upload image(s), video(s), and one audio file (e.g. background.mp3)
uploaded = files.upload()

# === 2. Create directories for organization ===
for folder in ('/content/images', '/content/videos', '/content/music'):
    os.makedirs(folder, exist_ok=True)

# === 3. Move each uploaded file into its folder ===
for fname in uploaded.keys():
    lower = fname.lower()
    if lower.endswith(('.jpg', '.jpeg', '.png')):
        shutil.move(fname, f'/content/images/{fname}')
    elif lower.endswith(('.mp4', '.mov', '.avi', '.mkv')):
        shutil.move(fname, f'/content/videos/{fname}')
    elif lower.endswith(('.mp3', '.wav', '.aac', '.ogg')):
        shutil.move(fname, f'/content/music/{fname}')
    else:
        print(f"Skipped unrecognized file type: {fname}")

# === 4. Define your file paths ===
image_files = sorted([os.path.join('/content/images', f) 
                      for f in os.listdir('/content/images')])
video_files = sorted([os.path.join('/content/videos', f) 
                      for f in os.listdir('/content/videos')])
music_files = sorted([os.path.join('/content/music', f) 
                      for f in os.listdir('/content/music')])

# === 5. Create ImageClips ===
image_clips = [
    ImageClip(img)
      .set_duration(3)         # each image holds for 3 seconds
      .resize(height=1080)     # scale to 1080p height (auto aspect)
      .set_fps(24)
    for img in image_files
]

# === 6. Create VideoClips (trimmed & resized) ===
video_clips = []
for vpath in video_files:
    clip = VideoFileClip(vpath)
    # take first 5 seconds or full length if shorter
    end = min(5, clip.duration)
    trimmed = clip.subclip(0, end).resize(height=1080).set_fps(24)
    video_clips.append(trimmed)

# === 7. Load your music track ===
if music_files:
    bg_audio = AudioFileClip(music_files[0])
    # optionally, you can loop or cut it to match the final duration
else:
    bg_audio = None
    print("No music file found in /content/music – final video will be silent.")

# === 8. Assemble all clips in order ===
# e.g. images → videos → repeat first image as outro
all_clips = image_clips + video_clips + ([image_clips[0]] if image_clips else [])

final = concatenate_videoclips(all_clips, method="compose")

# === 9. Mix in the background audio ===
if bg_audio:
    # trim or loop the audio to match final clip duration
    if bg_audio.duration < final.duration:
        # loop the audio
        loops = int(final.duration // bg_audio.duration) + 1
        bg_audio = concatenate_videoclips([bg_audio] * loops)
    bg_audio = bg_audio.subclip(0, final.duration)

    # combine original video audio (if any) with the bg track
    final_audio = CompositeAudioClip([final.audio.volumex(1.0), bg_audio.volumex(0.3)])
    final = final.set_audio(final_audio)

# === 10. Export the finished reel ===
output_path = "/content/Singapore_Trip_Reel_with_Music.mp4"
final.write_videofile(
    output_path,
    fps=24,
    codec="libx264",
    audio_codec="aac",
    temp_audiofile="temp-audio.m4a",
    remove_temp=True
)

print(f"✅ Finished rendering! Download your video here:\n{output_path}")
