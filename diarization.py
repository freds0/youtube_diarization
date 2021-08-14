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

    pipeline = torch.hub.load('pyannote/pyannote-audio', 'dia_ami')

    filename = basename(audio_filepath)
    folder = dirname(audio_filepath)
    output_json = join(folder, 'segments.json')

    test_file = {'uri': filename, 'audio': audio_filepath}

    diarization = pipeline(test_file)
    data = diarization.for_json()

    with open(output_json, 'w') as f:
        json.dump(data, f, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', default='', help="mp3 filepath")

    args = parser.parse_args()
    execute_diarization(args.input_file)


if __name__ == '__main__':
    main()
