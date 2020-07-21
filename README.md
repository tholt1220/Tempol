# Tempol
A flask application using librosa and ffmpeg to convert an mp3 file to a specific tempo. Developed to aid practicing musicians to lineup songs with a metronome.

### Installing dependencies 
Requirements are shown in requirements.txt. Additionally, ffmpeg and libsndfile1 need to be installed using apt-get. If deploying using Docker, the Dockerfile installs all pip and apt packages.
Boto3 is optionally needed if connecting to an AWS s3 container.

## Application Steps
Tempol is designed to run in a Dockerized Container or deployed to AWS elastic beanstalk.
 

### Step 1: File upload
Endpoint: `/upload`

The first step is to upload a file. Users have the option to upload their own audio file (.mp3 or .wav) or input a link from YouTube (Tempol will use youtube-dl to extract the audio).
Uploaded audio files are stored in
* uploads folder (./uploads)
* AWS s3 folder (access keys must be provided)


### Step 2: BPM Detection
Once a file is uploaded, it's URL path will be sent to `calculateBPM()`. Using the librosa beat detection algorithm, it will return the estimated BPM (float). 

Note: If uploading to AWS, use soundfile instead of librosa (soundfile supports reading stream from a URL instead of filepath)

### Step 3: Alter Tempo
Endpoint: `/convert`

The calculated tempo from Step 2 is displayed to the user, and the user will input a new tempo to convert the file to. This is sent to `alterTempo()`

Ffmpeg will speed up the original audio by a factor of `new_tempo / original_tempo`. For example, if the original tempo is 120 BPM and the desired tempo is 180 BPM, Ffmpeg will speed up the original audio by a factor of `180/120 = 1.5`
The converted file is stored in the uploads foler (either locally or in s3 bucket). The filename will have the target tempo appended (eg. mysong.mp3 -> mysong_130.mp3)

### Step 4: Playlists
Endpoint: `/playlistCRUD`

Users can create a playlist of songs for practice sessions. Features:
* Reorder (Move song up/down)
* Duplicate 
* Delete (file will be removed from uploads folder)

Playlists are represented as a dictionary session variable. Using cookies, different dictionaries are stored for each user.


