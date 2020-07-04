import librosa
import io
import soundfile as sf
import zipfile as zf
import os
from pydub import AudioSegment

# 1. Get the file path to the included audio example
# src = './Algorythm.mp3'
# dst = "test.wav"

ROOTDIR = os.getcwd()
src = os.path.join(ROOTDIR, "Algorythm.mp3")
dst = os.path.join(ROOTDIR, "test.wav")


# convert wav to mp3                                                            
sound = AudioSegment.from_mp3(src)
sound.export(dst, format="wav")

# stmp = io.BytesIO(filename.read())
# y, sr = sf.read(filename)

# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
y, sr = librosa.load(filename)

# 3. Run the default beat tracker
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

print('Estimated tempo: {:.2f} beats per minute'.format(tempo))

# 4. Convert the frame indices of beat events into timestamps
beat_times = librosa.frames_to_time(beat_frames, sr=sr)