# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) 2021 Frederico Oliveira fred.santos.oliveira(at)gmail.com
#
#
import argparse
import json
from os.path import basename, dirname, join
from pydub import AudioSegment
from download import download_from_youtube
from diarization import execute_diarization
from audio_segmentation import create_segments_list_from_json, create_audio_files_from_segments_list


def execute_pipeline(youtube_links_filepath, output_dir):
    """
    Execute diarization pipeline. (1) Download mp3 audio from youtube;, (2) Convert mp3 to wav; (3) Audio diarization; (4) Audio segmentation.
        Parameters:
        youtube_links_filepath (str): filepath of source file with youtube links list.
        output_dir (str): output folder.

        Returns:
        Boolean: returns True or False
    """

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
        # (1) Download audio from youtube
        #
        if youtube_link.startswith('https://'):
            mp3_audio_filepath = download_from_youtube(youtube_link, output_dir)
        else:
            continue

        if not mp3_audio_filepath:
            print("Error: Unable to download mp3 from youtube.")
            return False
        #
        # (2) Converting mp3 to wav
        #
        try:
            sound = AudioSegment.from_mp3(mp3_audio_filepath)
            wav_audio_filepath = mp3_audio_filepath.replace('.mp3', '.wav')
            sound.export(wav_audio_filepath, format="wav")
        except:
            print("Error: Unable to convert mp3 to wav.")
            return False
        #
        # (3) Audio diarization
        #
        json_path = execute_diarization(wav_audio_filepath)

        if not json_path:
            return False
        #
        # (4) Audio segmentation
        #
        segments_list = create_segments_list_from_json(json_path)
        filename_base = basename(wav_audio_filepath)

        output_segments_path = join(dirname(wav_audio_filepath), 'segments')
        r = create_audio_files_from_segments_list(wav_audio_filepath, filename_base, segments_list, output_segments_path)
        if not r:
            print("Error: Unable to create audio segments list.")
            return False

        r = create_audio_files_from_segments_list(wav_audio_filepath, filename_base, segments_list, output_segments_path)
        if not r:
            print("Error: Unable to create audio segments.")
            return False

        return True
        

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

    output_dir = args_data['videos_folder']
    youtube_links_filepath = args_data['youtube_list']

    r = execute_pipeline(youtube_links_filepath, output_dir)

    if r:
        print("Success!")
    else:
        print('Fail!')

if __name__ == '__main__':
    main()

