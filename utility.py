import librosa
import os
from pydub import AudioSegment
import sys
import ffmpeg
# import ntpath

# import soundfile as sf
# import io
# from urllib.request import urlopen

# from application import s3, application
# from subprocess import Popen, PIPE


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

# bucket_name = application.config["S3_BUCKET"]


def calcluateBPM(src):
	#soundfile only supports .wav
	#SO convert .mp3 to .wav using ffmpeg
	# src_filename, src_filetype = os.path.splitext(src)
	# if src_filetype == '.mp3' or src_filetype ==".webm":
	# 	print("mp3 to wav:")
	# 	output, _ = (
	# 		ffmpeg.input(src)
	# 		.output('pipe:', format='wav')
	# 		.run(capture_stdout=True)
	# 	)

	# 	#upload .wav to s3 bucket
	# 	filename = ntpath.basename(src_filename) + ".wav"
	# 	print("uploading " + filename)
	# 	src = upload_bytes_to_s3(io.BytesIO(output), filename, bucket_name)

	# 	#delete .mp3 or .wav file from s3 bucket
	# 	src_filename = filename.replace(".wav", src_filetype)
	# 	delete_from_s3(src_filename, bucket_name)

	
	try:
		#read from local 
		y, sr = librosa.load(src)

		# #read from s3 URL
		# audio_stream = io.BytesIO(urlopen(src).read())
		# audio_stream.seek(0)
		# y, sr = sf.read(audio_stream)
		# #soundfile may return shape (n,2), but librosa expects (n,)
		# if(y.shape[1] > 1):
		# 	#to_mono: (2,n) -> (n,)
		# 	y = librosa.to_mono(y.transpose())

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

	#local files
	filename, filetype = os.path.splitext(src)
	new_name = filename + "_" + floatToString(goal)
	
	while os.path.isfile(new_name + filetype):
		print(new_name + " is taken")
		new_name += "_new"
		
	new_name += filetype

	try:
		input = ffmpeg.input(src)
		input = ffmpeg.filter_(input, 'atempo', factor)
		output = ffmpeg.output(input, new_name)
		ffmpeg.run(output)
	except Exception as e:
		print("Conversion Error: ", e)

	# remove original file
	os.remove(src)
	

	#s3 bucket

	# #src_filename is of the form http://bucket-name.../name.wav
	# src_filename, filetype = os.path.splitext(src)
	# #name
	# src_filename = ntpath.basename(src_filename)
	# #name_120
	# filename = src_filename + "_" + floatToString(goal)

	# #if filename is already in the bucket, append "_new" to the end
	# s3_files = [file["Key"] for file in s3.list_objects(Bucket=bucket_name)["Contents"]]
	# while (filename + filetype) in s3_files:
	# 	filename += "_new"

	# #name_120.wav
	# filename += filetype
	# #name.wav
	# src_filename += filetype

	# print("FILENAME:" , filename)

	# #run ffmpeg in subprocess, feed stdout into output
	# output, _ = (
	# 	ffmpeg
    # 	.input(src)
	# 	.filter_('atempo', factor)
    # 	.output('pipe:', format='wav')
    # 	.run(capture_stdout=True)
	# )

	# print("DONE PROCESSING")

	# #cast output as FileObj, send to s3 bucket, get new filename 
	# new_name = upload_bytes_to_s3(io.BytesIO(output), filename, bucket_name)
	
	# #delete original file from s3 bucket
	# delete_from_s3(src_filename, application.config["S3_BUCKET"])
	
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

# def delete_from_s3(filename, bucketname):
# 	try:
# 		response = s3.delete_object(
# 			Bucket = bucketname,
# 			Key = filename
# 		)
# 		print("removed ", filename)
# 	except Exception as e:
# 		# This is a catch all exception, edit this part to fit your needs.
# 		print("Something Happened: ", e)
# 		return e
# 	return


# def upload_bytes_to_s3(bytes, filename, bucket_name, acl="public-read"):
# 	try:

# 		s3.upload_fileobj(
# 			bytes,
# 			bucket_name,
# 			filename,
# 			ExtraArgs={
# 				"ACL": acl
# 			}
# 		)

# 	except Exception as e:
# 		# This is a catch all exception, edit this part to fit your needs.
# 		print("Something Happened: ", e)
# 		return e

# 	return "{}{}".format(application.config["S3_LOCATION"], filename)