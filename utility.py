import librosa
import os
from pydub import AudioSegment
import sys
from pathlib import Path
import ffmpeg

import soundfile as sf
import io
from urllib.request import urlopen


#     argc = len(sys.argv)
#     if argc == 1:
#         print("Error: No file given")
#         return 
#     elif argc > 2:
#         print("Error: Multiple files given")
#         return 
#     else:
#         mp3_file = sys.argv[1]

'''May be unnecessary
src = sys.argv[1]
if src.endswith('.mp3'):
    sound = AudioSegment.from_mp3(src)
elif src.endswith('.wav'):
    sound = AudioSegment.from_wav(src)
else:
    print("Error: only supports .mp3 or .wav types")
'''

def calcluateBPM(src):
	print(src)
	# 2. Load the audio as a waveform `y`
	#    Store the sampling rate as `sr`
	
	try:
		#read from local 
		#y, sr = librosa.load(src)
		#read from s3 URL
		y, sr = sf.read(io.BytesIO(urlopen(src).read()))

	except Exception as e :
		print("Unable to find file")
		print(e)
		return 0

	# 3. Run the default beat tracker
	# print("Calculating original tempo...")
	original_tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

	# print('Estimated tempo: {:.2f} beats per minute'.format(original_tempo))
	print(original_tempo)
	return original_tempo
	# # 4. Convert the frame indices of beat events into timestamps
	# beat_times = librosa.frames_to_time(beat_frames, sr=sr)
	# print(beat_times)

def floatToString(f): #replace decimal point with underscore. If whole number, return only whole num
	if f - int(f) == 0:
		return str(int(f))
	else:
		return str(f).replace('.', '_')

def pathToURI(pathString):
	return pathString.replace('\\', '/')


def alterTempo(src, original_tempo, goal):
	factor = float(goal) / original_tempo
	print("\nGoal Tempo: " + str(goal))
	print("Altering tempo by factor of " + str(factor) + "...\n\n")


	filename, filetype = os.path.splitext(src)
	new_name = filename + "_" + floatToString(goal)

	if os.path.isfile(new_name + filetype):
		print(new_name + " is taken")
		new_name = new_name + "_new" + filetype
	else:
		new_name = new_name + filetype
	
	input = ffmpeg.input(src)
	input = ffmpeg.filter_(input, 'atempo', factor)
	output = ffmpeg.output(input, new_name)
	ffmpeg.run(output)
	
	#remove original file
	os.remove(src)
	return new_name

def calcAndAlter(filename, targetBPM):
	original_tempo = calcluateBPM(filename)
	if original_tempo > 0:
		new_name = alterTempo(filename, original_tempo, targetBPM)
		return new_name

	return 'FAILED'


if __name__ == "__main__":
 	# calcAndAlter(sys.argv[1], sys.argv[2])
	 pass

