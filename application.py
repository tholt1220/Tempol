import os
import sys
import utility
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, jsonify, Response, session
from werkzeug.utils import secure_filename
import ntpath
import json
import youtube_dl
import boto3
from config import S3_KEY, S3_SECRET, S3_BUCKET
from contextlib import redirect_stdout
import io

upload_folder = 'uploads'
allowed_extensions = {'mp3', 'wav'}
application = Flask(__name__, template_folder='templates')
application.config['upload_folder'] = upload_folder
application.secret_key = 'secret key'

application.config.from_object("config")
s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET
)

bucket_name = application.config["S3_BUCKET"]
def filetype(filename):
	return filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
	return '.' in filename and filetype(filename) in allowed_extensions

#DB CRUD OPERATIONS
@application.route('/playlistCRUD', methods = ['GET'])
def get_playlist():
	# playlist = playlist.objects().to_json
	# return Response(playlist, mimetype ="application/json", status = 200)
	return jsonify(session['playlist'])

@application.route('/playlistCRUD', methods=['POST'])
def addSong():
	song = request.values.to_dict()
	song['id'] = session['songCounter']
	song['trackNumber'] = len(session['playlist']) + 1
	session['songCounter'] += 1
	session['playlist'].append(song)
	session.modified = True
	return redirect(url_for('render_playlist')) #go to playlist
	
@application.route('/playlistCRUD/<id>', methods=['PUT'])
def update_song(id):
	song = request.get_json()
	session['playlist'][id] = song
	return jsonify(session['playlist'][id]), 200

@application.route('/playlistCRUD/<id>', methods=['DELETE'])
def delete_song(id):
	return_msg = "Nothing Deleted" , 204
	#Find song with id, remove it from playlist and delete it from files
	for i in range(len(session['playlist'])):
		if session['playlist'][i]['id'] == int(id):
			trackNumber = session['playlist'][i]['trackNumber']
			filename = session['playlist'][i]['filename']
			del session['playlist'][i]
			deleteFile(filename)
			session.modified = True
			return_msg =  id + ' Deleted', 200
			break
	#decrement track number of each song with higher track number 
	for i in range(len(session['playlist'])):
		if session['playlist'][i]['trackNumber'] >= trackNumber:
			session['playlist'][i]['trackNumber'] -= 1
	return return_msg

@application.route('/playlistUp/<trackNum>')
def playlistUp(trackNum): #move trackNum Up
	if int(trackNum) == 1 or int(trackNum) == len(session['playlist']) + 1:
		return "no swap", 200

	swapIndex1, swapIndex2 = -1, -1
	for i in range(len(session['playlist'])):
		if session['playlist'][i]['trackNumber'] == int(trackNum):
			session['playlist'][i]['trackNumber'] -= 1
			swapIndex1 = i
			session.modified = True
		elif session['playlist'][i]['trackNumber'] == int(trackNum) - 1:
			session['playlist'][i]['trackNumber'] += 1
			session.modified= True
			swapIndex2 = i

	if swapIndex1 != -1 and swapIndex2 != -1: 
		session['playlist'][swapIndex1], session['playlist'][swapIndex2] = session['playlist'][swapIndex2], session['playlist'][swapIndex1]

	return 'swapped', 200

@application.route('/duplicateSong/<id>')
def duplicateSong(id):
	for i in range(len(session['playlist'])):
		if session['playlist'][i]['id'] == int(id):
			tempSong = session['playlist'][i].copy()
			break

	tempSong['id'] = session['songCounter']
	tempSong['trackNumber'] = len(session['playlist']) + 1
	session['songCounter'] += 1
	session['playlist'].append(tempSong)
	session.modified = True
	return '' , 204 #creating view function without returning response in flask

	
def deleteFile(filename):
	for song in session['playlist']:
		if filename in song.values():
			print(filename + " not deleted")
			return
	#song is not used anywhere else, so delete it 
	#filekey is the basename of the full s3 URL:
	file_key = ntpath.basename(filename)
	try:
		utility.delete_from_s3(file_key, application.config['S3_BUCKET'])
	except:
		print("unable to remove ")
	
	


#END DB CRUD OPERATIONS

@application.route('/playlist', methods = ['GET'])
def render_playlist():
	return render_template('playlist.html', playlist=session['playlist'])

@application.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(application.config['upload_folder'], filename)

@application.route('/tempo',methods =['GET', 'POST'])
def tempo():
	if request.method == 'POST':
		print('Incoming..')
		print(request.get_data())
		filename = dataFromJSON(request.get_data(), 'filename')
		return filename, 200
	else: #request is a get
		message = {'greeting': 'Hello from flask!'}
		return jsonify(message)

@application.route('/error')
def error():
	print("ERROR")
	return render_template('error.html')


@application.route('/convert', methods = ['POST'])
def newFile():
	if request.method == 'POST':
		filepath = request.form['filepath']
		original_tempo = request.form['original_tempo']
		target_tempo = request.form['target']
		new_filename = utility.alterTempo(filepath, float(original_tempo), float(target_tempo))
		songname = request.form['songname']
		return render_template('play.html', new_filename=new_filename, filetype=filetype(new_filename), songname=songname, tempo=target_tempo)

@application.route('/upload', methods = [ 'POST'])
def upload():	
	if request.method =='POST':
		print(request)
		if 'uploadFile' in request.form: #user inputs a file
			if 'file' not in request.files:
				return redirect(request.url)

			file = request.files['file']
			if file.filename == "":
				flash('No selected file')
				return redirect(request.url)
			if file and allowed_file(file.filename):
				flash('file selected')
				file.filename = secure_filename(file.filename)
				filename = file.filename
				#to upload to local machine:
				# file.save(os.path.join(application.config['upload_folder'], filename)) 
				# filepath = os.path.join(application.config['upload_folder'], filename)

				#to upload to s3:
				filepath = str(upload_file_to_s3(file, bucket_name))

		elif 'uploadYT' in request.form:
			filename, filepath =  downloadLink(request.form['link'])
			if filename is None:
				return redirect(url_for('error'))


		original_BPM = utility.calcluateBPM(filepath)
		
		print('HERE')
		songName = request.form.get('songName')
		if songName is None:
			songName = filename
		
		#if deploying on AWS, only .wav is supported
		filename = filename.replace(".mp3", ".wav")
		filepath = filepath.replace(".mp3", ".wav")
		filename = filename.replace(".webm", ".wav")
		filepath = filepath.replace(".webm", ".wav")
	
		return render_template('convert.html', tempo=original_BPM, filename=filename, filepath=filepath, songName=songName)
	return

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

def downloadLink(link):
	# FOR LOCAL UPLOADS
	# ydl_opts = {
	# 	'format': 'bestaudio/wav',       
   	# 	'noplaylist' : True,        
    # 	'progress_hooks': [my_hook],
	# 	'postprocessors': [{
	# 		'key': 'FFmpegExtractAudio',
	# 		'preferredcodec': 'wav',
	# 		'preferredquality': '192',
	# 	}],
	# 	'outtmpl': os.path.join(application.config['upload_folder'], '%(title)s.%(ext)s')
	# }
	# try:
	# 	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	# 		ydl.download([link])
	# 		result = ydl.extract_info(link, download=False)
	# 		unsecure_filename = ydl.prepare_filename(result)
	# except:
	# 	return None, None
	
	# #output from ydl
	# unsecure_filepath = unsecure_filename.replace('.webm', '.mp3')
	# unsecure_filename = unsecure_filename.replace('uploads\\', '')

	# print(unsecure_filename, unsecure_filepath)
	# print(os.path.isfile(unsecure_filepath))


	# #video title may have illegal characters
	# secure_fileName = secure_filename(unsecure_filename)
	# secure_filepath = os.path.join(application.config['upload_folder'], secure_fileName)

	# #rename with secure filepath
	# try:
	# 	os.rename(unsecure_filepath, secure_filepath)
	# except: #if file already exists, remove it and add it again
	# 	os.remove(secure_filepath)
	# 	os.rename(unsecure_filepath, secure_filepath)

	# FOR s3 UPLOADS
	ydl_opts = {
		'format': 'webm',       

	}
	try:
		cmd = "youtube-dl -f 251 " + link + " -o -"
		print(cmd)
		proc = utility.Popen(cmd, stdout=utility.PIPE)
		output, _ = proc.communicate()
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			result = ydl.extract_info(link, download=False)
			yt_filename = secure_filename(ydl.prepare_filename(result))
	except Exception as e:
		print("An Error Occured: ", e)
		return None, None
	

	filename, filetype = os.path.split(yt_filename)
	#if filename is already in the bucket, append "_new" to the end
	s3_files = [file["Key"] for file in s3.list_objects(Bucket=bucket_name)["Contents"]]
	while (filename + filetype) in s3_files:
		filename += "_new"

	yt_filename = filename + filetype
	print(yt_filename)

	yt_filepath = utility.upload_bytes_to_s3(io.BytesIO(output), yt_filename, bucket_name)
	print(yt_filepath)

	return yt_filename, yt_filepath

def dataFromJSON(JSONstring, key):
	JSONDict = json.loads(JSONstring)
	return JSONDict[key]

def pathToURI(pathString):
	return pathString.replace('\\', '/')

@application.route('/', methods = ['GET', 'POST'])
def main():
	if request.method =='GET':
		print(session)
		if not bool(session):
			session['playlist'] = []
			session['songCounter'] = 0
			print(session)
		else:
			print(session['playlist'])
			print(session['songCounter'])
		return render_template('upload.html')

def upload_file_to_s3(file, bucket_name, acl="public-read"):
	try:

		s3.upload_fileobj(
			file,
			bucket_name,
			file.filename,
			ExtraArgs={
				"ACL": acl,
				"ContentType": file.content_type
			}
		)

	except Exception as e:
		# This is a catch all exception, edit this part to fit your needs.
		print("Something Happened: ", e)
		return e

	return "{}{}".format(application.config["S3_LOCATION"], file.filename)

if __name__ == '__main__':
    application.run()