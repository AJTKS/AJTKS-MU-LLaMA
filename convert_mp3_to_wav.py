import os
from pydub import AudioSegment

# Function to remove whitespace from file names
def remove_whitespace(directory):
    for filename in os.listdir(directory):
        if ' ' in filename:
            os.rename(os.path.join(directory, filename), os.path.join(directory, filename.replace(' ', '')))

# Function to convert mp3 to wav
def convert_mp3_to_wav(mp3_directory, wav_directory):
    for filename in os.listdir(mp3_directory):
        if filename.endswith('.mp3'):
            audio = AudioSegment.from_mp3(os.path.join(mp3_directory, filename))
            wav_filename = filename[:-4] + '.wav'  # Change the extension to .wav
            audio.export(os.path.join(wav_directory, wav_filename), format='wav')

# Define your directories
input_directory = '/home/elicer/MERT/music_source/music_mp3'
output_directory = '/home/elicer/MERT/music_source/music_wav'

# Remove whitespace from file names in the input directory
remove_whitespace(input_directory)

# Convert mp3 files to wav and save to the output directory
convert_mp3_to_wav(input_directory, output_directory)
