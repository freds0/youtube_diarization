# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) 2021 Frederico Oliveira fred.santos.oliveira(at)gmail.com
#
#
import argparse
import json
from pydub import AudioSegment

from download import download_from_youtube
from diarization import execute_diarization

def diarization_files_list():
    try:
        f = open(args.input_file)
        content_file = f.readlines()
    except IOError:
      print("Error: File {} does not appear to exist.".format(input_file))
      return False
    else:
        f.close()

    for youtube_link in content_file:

        if youtube_link.startswith('https://'):
            download_from_youtube(youtube_link, args.output_dir)


def execute_pipeline(args_data):

    output_dir = args_data['videos_folder']
    youtube_links_filepath = args_data['youtube_list']
    try:
        f = open(youtube_links_filepath)
        youtube_links_list = f.readlines()
    except IOError:
      print("Error: File {} does not appear to exist.".format(links_filepath))
      return False
    else:
        f.close()

    for youtube_link in youtube_links_list:

        #
        # Download audio from youtube
        #
        if youtube_link.startswith('https://'):
            #mp3_audio_filepath = download_from_youtube(youtube_link, output_dir)
            mp3_audio_filepath = 'output/videos/h7pRwmvWN7g/h7pRwmvWN7g.mp3'
        #
        # Audio diarization
        #
        if mp3_audio_filepath:
            # Convert mp3 to wav
            sound = AudioSegment.from_mp3(mp3_audio_filepath)
            wav_audio_filepath = mp3_audio_filepath.replace('.mp3', '.wav')
            sound.export(wav_audio_filepath, format="wav")
            execute_diarization(wav_audio_filepath)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.json', help="Json config file.")
    parser.add_argument('--output_dir', default='output', help='Directory to save downloaded audio and transcript files.')

    args = parser.parse_args()

    try:
        with open(args.config, "r") as jsonfile:
            args_data = json.load(jsonfile)
            print("Read {} successful".format(args.config))
    except IOError:
      print("Error: File {} does not appear to exist.".format(args.config))
      return False
    else:
        jsonfile.close()


    execute_pipeline(args_data)

if __name__ == '__main__':
    main()

