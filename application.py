import os
import sys
import utility
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, jsonify, Response, session
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import youtube_dl
import boto3

upload_folder = 'uploads'
allowed_extensions = {'mp3', 'wav'}
application = Flask(__name__, template_folder='templates')
application.config['upload_folder'] = upload_folder
BUCKET = "elasticbeanstalk-us-west-1-064202757067"
application.secret_key = 'secret key'

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
	print(filename + " deleted")
	try:
		os.remove(filename)
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
		return render_template('play.html', new_filename=utility.pathToURI(new_filename), filetype=filetype(new_filename), songname=songname, tempo=target_tempo)

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
				filename = secure_filename(file.filename)
				# file.save(os.path.join(application.config['upload_folder'], filename))
				upload_file(f"uploads/{file.filename}", BUCKET) #upload to AWS using boto3
				filepath = os.path.join(application.config['upload_folder'], filename)
		elif 'uploadYT' in request.form:
			filename, filepath =  downloadLink(request.form['link'])
			if filename is None:
				return redirect(url_for('error'))


		original_BPM = utility.calcluateBPM(filepath)
		
		print('HERE')
		songName = request.form.get('songName')
		if songName is None:
			songName = filename
	
		return render_template('convert.html', tempo=original_BPM, filename=filename, filepath=filepath, songName=songName)
	return

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')

def downloadLink(link):
	ydl_opts = {
		'format': 'bestaudio/best',       
   		'noplaylist' : True,        
    	'progress_hooks': [my_hook],
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
		'outtmpl': os.path.join(application.config['upload_folder'], '%(title)s.%(ext)s')
	}
	try:
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([link])
			result = ydl.extract_info(link, download=False)
			unsecure_filename = ydl.prepare_filename(result)
	except:
		return None, None
	
	#output from ydl
	unsecure_filepath = unsecure_filename.replace('.webm', '.mp3')
	unsecure_filename = unsecure_filename.replace('uploads\\', '')

	print(unsecure_filename, unsecure_filepath)
	print(os.path.isfile(unsecure_filepath))


	#video title may have illegal characters
	secure_fileName = secure_filename(unsecure_filename)
	secure_filepath = os.path.join(application.config['upload_folder'], secure_fileName)

	#rename with secure filepath
	try:
		os.rename(unsecure_filepath, secure_filepath)
	except: #if file already exists, remove it and add it again
		os.remove(secure_filepath)
		os.rename(unsecure_filepath, secure_filepath)


	print(secure_filepath)
	return secure_fileName, secure_filepath

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

def upload_file(file_name, bucket):
    """
    Function to upload a file to an S3 bucket
    """
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)

    return response



if __name__ == '__main__':
    application.run()