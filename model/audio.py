import librosa
import os
from pydub import AudioSegment
import sys

#     argc = len(sys.argv)
#     if argc == 1:
#         print("Error: No file given")
#         return 
#     elif argc > 2:
#         print("Error: Multiple files given")
#         return 
#     else:
#         mp3_file = sys.argv[1]

src = sys.argv[1]
# convert wav to mp3
if src.endswith('.mp3'):
    sound = AudioSegment.from_mp3(src)
elif src.endswith('.wav'):
    sound = AudioSegment.from_wav(src)
else:
    print("Error: only supports .mp3 or .wav types")


# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
y, sr = librosa.load(src)

# 3. Run the default beat tracker
print("Calculating original tempo...")
original_tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

print('Estimated tempo: {:.2f} beats per minute'.format(original_tempo))

# # 4. Convert the frame indices of beat events into timestamps
# beat_times = librosa.frames_to_time(beat_frames, sr=sr)
# print(beat_times)

if len(sys.argv) >= 2:
	goal = sys.argv[2]
	factor = float(goal) / original_tempo
	print("\nGoal Tempo: " + goal)
	print("Altering tempo by factor of " + str(factor) + "...\n\n")


	filename, filetype = os.path.splitext(src)
	new_name = filename + "_" + str(goal) + filetype
	command = 'ffmpeg -i %s -filter:a "atempo=%f" -vn %s' %(src, factor, new_name)
	os.system('cmd /c "%s"'%command)
print("Done.")