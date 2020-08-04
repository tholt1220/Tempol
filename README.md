# Tempol
A flask application using librosa and ffmpeg to convert an mp3 file to a specific tempo. Developed to aid practicing musicians to lineup songs with a metronome.

### Installing dependencies 
Requirements are shown in requirements.txt. Additionally, ffmpeg and libsndfile1 need to be installed using apt-get. If deploying using Docker, the Dockerfile installs all pip and apt packages.
Boto3 is optionally needed if connecting to an AWS s3 container.

## Running Tempol
Tempol can be cloned and run on a local machine. Simply clone the repository and install the required packages.

Once all required packages are installed, execute `python application.py` to run the application on localhost:5000 (port number can be specified in `application.py`. Consult flask documentation)
If running on local machine, all file uploads will be directed to the folder ./uploads

## API
### `/playlist`
#### Methods : GET

 This endpoint is for rendering the view to display the current playlist
  * GET
  
    Render template to display the current playlist
    * Parameters: None
    * Return: rendered template `playlist.html`
### `/convert`
#### Methods : POST

 This endpoint is forconverting the original audio to the specified tempo and rendering the view to play the modified audio.
  * POST
  
    Alter the tempo of the file, save into a new file, and render the template to play the modified audio
    * Parameters: None
    * Return: rendered template for `play.html`
    
### `/upload`
#### Methods : POST

 This endpoint is for handling file uploads. It handles these directly (if user inputs a filename) or via youtube-dl (if user inputs a youtube-link)
  * POST
  
    Upload file, calculate tempo, render template to display calculated tempo
    * Parameters: trackNumber
    * Return: rendered template for `convert.html`


### `/playlistCRUD`
#### Methods : GET | POST | PUT | DELETE

 This endpoint is for editing the list of songs that have already been converted. 
 * GET 
 
   Get current playlist
   * Parameters: None
   * Return: a json object of the current playlist
 
  * POST
  
    Add song to current playlist
    * Parameters: None
    * Return: redirected URL for new playlist
    
  * PUT
  
    Update a song that's already in the playlist
    * Parameters: song ID
    * Return: a json object of the current playlist
    
  * DELETE
  
    Delete a song that's already in the playlist
    * Parameters: song ID
    * Return: a json object of the current playlist 
### `/playlistUp/<trackNumber>`
#### Methods : POST

 This endpoint is for reordering the current list of songs
  * POST
  
    Swap the selected song with the song one above it (move the song up in the playlist)
    * Parameters: trackNumber
    * Return: None
### `/duplicateSong<id>`
#### Methods : POST

 This endpoint is for adding a duplicate of an existing song to the current playlist
  * POST

    Create a song object, append it to the list of songs
    * Parameters: id
    * Return: None
 

## Application Steps
Tempol is designed to run in a Dockerized Container or deployed to AWS elastic beanstalk. For testing purposes, it can also be deployed locally.


### Step 1: File upload
Endpoint: `/upload`

The first step is to upload a file. Users have the option to upload their own audio file (.mp3 or .wav) or input a link from YouTube (Tempol will use youtube-dl to extract the audio).
Uploaded audio files are stored in
* uploads folder (.uploads)
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


