# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) 2021 Frederico Oliveira fred.santos.oliveira(at)gmail.com
#
#
import torch
from os.path import basename, dirname, join
import json
import argparse


def execute_diarization(audio_filepath):
    """
    Execute diarization pipeline using pyannote-audio. Source: https://github.com/pyannote/pyannote-audio
        Parameters:
        audio_filepath (str): mp3 audio filepath.

        Returns:
        String: returns json filepath or False.
    """
    pipeline = torch.hub.load('pyannote/pyannote-audio', 'dia_ami')

    filename = basename(audio_filepath)
    folder = dirname(audio_filepath)
    output_json = join(folder, 'segments.json')

    input_diarization_file = {'uri': filename, 'audio': audio_filepath}

    try:
        diarization = pipeline(input_diarization_file)
        data = diarization.for_json()

    except:
        print("Error: Unable to execute diarization pipeline.")
        return False

    try:
        with open(output_json, 'w') as f:
            json.dump(data, f, ensure_ascii=False)

    except TypeError:
        print("Error: Unable to dump to the json file")
        return False

    return output_json


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', default='', help="mp3 filepath")

    args = parser.parse_args()
    execute_diarization(args.input_file)


if __name__ == '__main__':
    main()
