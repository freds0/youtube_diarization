#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) 2021 Frederico Oliveira fred.santos.oliveira(at)gmail.com
#
# Adapted from https://gist.github.com/keithito/771cfc1a1ab69d1957914e377e65b6bd from Keith Ito: kito@kito.us
#
import argparse
import os
import json
from pydub import AudioSegment
from collections import OrderedDict
import glob
from scipy.io.wavfile import write
# import torchaudio
import librosa
import numpy as np

class Segment:
    """
    Linked segments lists
    """
    def __init__(self, begin, end, filename):
        self.begin = begin
        self.end = end
        self.text = ''
        self.next = None
        self.filename = filename
        self.gap = 0 # gap between segments (current and next)

    def set_next(self, next):
        self.next = next
        self.gap = next.begin - self.end

    def set_filename_and_id(self, filename, id):
        self.filename = filename
        self.id = id

    def merge_from(self, next):
        # merge two segments (current and next)
        self.next = next.next
        self.gap = next.gap
        self.end = next.end

    def duration(self, sample_rate):
        return (self.end - self.begin - 1) / sample_rate


def create_segments_list_from_json(json_path):
    """
    Creates a list of segments from the json file resulting from pyannote processing.
    """

    head = None
    with  open(json_path) as jfile :
        data = json.load(jfile)
        wav_filename = data['uri'].split('.')[0]
        for i, fragment in enumerate(data['content']):
            begin = fragment['segment']['start']*1000
            end   = fragment['segment']['end']*1000
            filename = '{}-{}-{}-{:04d}.wav'.format(wav_filename, fragment['label'], fragment['track'], i)

            # Build a segment list
            segment = Segment(begin, end, filename)
            if head is None:
                head = segment
            else:
                prev.set_next(segment)
            prev = segment

    return head


def create_audio_files_from_segments_list(audio_file, filenames_base, head_list, output_dir):
    """
    Segments an audio file from a segment list, saving the files in a folder.
        Parameters:
        audio_file (str): filepath of source audio file.
        filenames_base (str): Filename prefix of audio segmented files.
        head_list (str): Reference of the linked list of segments.
        output_dir (str): Folder to save segmented audio files.

        Returns:
        String: returns True or False
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    sound = AudioSegment.from_file(audio_file)
    curr = head_list
    i = 1
    while curr is not None:
        begin = curr.begin
        end = curr.end
        text = curr.text
        audio_segment = sound[begin:end]
        #filename = '{}-{:04d}.wav'.format(filenames_base, i)
        #filename = curr.filename + '.wav'
        curr.set_filename_and_id(curr.filename, i)
        filepath = os.path.join(output_dir, curr.filename)
        try:
            audio_segment.export(filepath, 'wav')
        except IOError:
          print("Error: Writing audio file {} problem.".format(filepath))
          return False
        else:
            curr = curr.next
            i += 1
    return True


def create_metadata_from_segments_list(head_list, output_file):
    """
    Creates a csv file following the template: "filename | text"
        Parameters:
        head_list (str): Reference of the linked list of segments.
        output_file (str): csv output filename.

        Returns:
        String: returns True or False
    """
    separator = '|'
    curr = head_list
    try:
        f = open(output_file, "w")
        while curr is not None:
            text = curr.text
            filename = curr.filename.replace('.mp3', '')
            f.write(filename + separator + text[0] + '\n')
            curr = curr.next
        f.close()
    except IOError:
        print("Error: creating File {} problem.".format(output_file))
        return False
    return True


def segment_audio(audio_path, json_path, output_path, metadata_output_file, filename_base):
    """
    Performs the segmentation of the audio files and the creation of the csv file.
        Parameters:
        audio_path (str): filepath of source audio file.
        json_path (str): json file resulting from aeneas processing.
        output_path (str): Folder to save segmented audio files.
        metadata_output_file (str): csv output filename.
        filename_base (str): Filename prefix of audio segmented files.

        Returns:
        String: returns True or False
    """
    segments_list = create_segments_list_from_json(json_path)

    if not create_audio_files_from_segments_list(audio_path, filename_base, segments_list, output_path):
        return False
    return True


def segment_wav(wav, threshold_db, filename):
    '''
    Segment audio file and return a segment linked list
    '''
    # Find gaps at a fine resolution:
    parts = librosa.effects.split(wav, top_db=threshold_db, frame_length=1024, hop_length=256)

    # Build up a linked list of segments:
    head = None
    prev = None

    for begin, end in parts:
        segment = Segment(begin, end, filename)
        if head is None:
            head = segment
        else:
            prev.set_next(segment)
        prev = segment

    return head


def find_best_merge(segments, sample_rate, max_duration, max_gap_duration):
    '''
    Find small segments that can be merged by analyzing max_duration and max_gap_duration
    '''
    best = None
    best_score = 0
    s = segments
    while s.next is not None:
        gap_duration = s.gap / sample_rate
        merged_duration = (s.next.end - s.begin) / sample_rate
        if gap_duration <= max_gap_duration and merged_duration <= max_duration:
            score = max_gap_duration - gap_duration
            if score > best_score:
                best = s
                best_score = score
        s = s.next
    return best


def find_segments(filename, wav, sample_rate, min_duration, max_duration, max_gap_duration, threshold_db):
    '''
    Given an audio file, creates the best possible segment list
    '''

    # Segment audio file
    segments = segment_wav(wav, threshold_db, filename)
    # Merge until we can't merge any more
    while True:
        best = find_best_merge(segments, sample_rate, max_duration, max_gap_duration)
        if best is None:
            break
        best.merge_from(best.next)

    # Convert to list
    result = []
    s = segments
    while s is not None:
        result.append(s)
        # Create a errors file
        if s.duration(sample_rate) < min_duration and s.duration(sample_rate) > max_duration:
            with open(os.path.join(os.path.dirname(__file__), "erros.txt"), "a") as f:
                f.write(filename+"\n")
        # Extend the end by 0.2 sec as we sometimes lose the ends of words ending in unvoiced sounds.
        s.end += int(0.2 * sample_rate)
        s = s.next
    return result


def load_filenames(input_folder):
    '''
    Given an folder, creates a wav file alphabetical order dict
    '''
    mappings = OrderedDict()
    for filepath in glob.glob(os.path.join(input_folder + "/*.wav")):
        filename = os.path.basename(filepath).split('.')[0]
        mappings[filename] = filepath
    return mappings


def build_segments(input_folder, output_folder, output_filename, min_duration = 15, max_duration = 30, threshold = 32.0, max_gap_duration = 5.0, sample_rate = 22050):
    '''
    Build best segments of wav files
    '''
    os.makedirs(output_folder, exist_ok=True)
    # Initializes variables
    avg_duration = 0
    all_segments = []
    total_duration = 0
    filenames = load_filenames(input_folder)

    for i, (file_id, filename) in enumerate(filenames.items()):
        print('Loading %s: %s (%d of %d)' % (file_id, filename, i+1, len(filenames)))
        wav, sr = librosa.load(filename, sr=sample_rate)
        print(' -> Loaded %.1f min of audio. Splitting...' % (len(wav) / sr / 60))

        # Find best segments
        segments = find_segments(filename, wav, sr, min_duration, max_duration, max_gap_duration, threshold)
        duration = sum((s.duration(sr) for s in segments))
        total_duration += duration

        # Create records for the segments
        output_filename = output_filename if output_filename else file_id
        j = 0
        for s in segments:
            all_segments.append(s)
            s.set_filename_and_id(filename, '%s-%04d' % (output_filename, j))
            j = j + 1

        print(' -> Segmented into %d parts (%.1f min, %.2f sec avg)' % (
            len(segments), duration / 60, duration / len(segments)))

        # Write segments to disk:
        for s in segments:
            segment_wav = (wav[s.begin:s.end] * 32767).astype(np.int16)
            out_path = os.path.join(output_folder, '%s.wav' % s.id)
            write(out_path, sr, segment_wav)

            duration += len(segment_wav) / sr
            duration_segment = len(segment_wav) / sr
            if duration_segment > max_duration:
                max_duration = duration_segment

            avg_duration = avg_duration + duration_segment
        print(' -> Wrote %d segment wav files' % len(segments))
        print(' -> Progress: %d segments, %.2f hours, %.2f sec avg' % (
            len(all_segments), total_duration / 3600, total_duration / len(all_segments)))

        print('Writing metadata for %d segments (%.2f hours)' % (len(all_segments), total_duration / 3600))
        with open(os.path.join(output_folder, 'segments.csv'), 'w') as f:
            for s in all_segments:
                f.write('%s|%s|%d|%d\n' % (s.id, s.filename, s.begin, s.end))

        print('Mean: %f' %( avg_duration / len(all_segments) ))
        print('Max: %d' %(max_duration ))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default='./')
    parser.add_argument('--audio_file', default='audio.wav', help='Filename to input audio file')
    parser.add_argument('--filename_base', default='audio', help='Filename base of splited audios file. Ex. audio-0001.wav')
    parser.add_argument('--json_file', default='teste.json', help='Filename of input json file')
    parser.add_argument('--output_dir', default='output', help='Output dir')
    parser.add_argument('--metadata_file', default='metadata.csv', help='Filename to metadata output file')
    args = parser.parse_args()

    audio_path = os.path.join(args.base_dir, args.audio_file)
    json_path = os.path.join(args.base_dir, args.json_file)
    output_dir = os.path.join(args.base_dir, args.output_dir)
    metadata_output_file = os.path.join(args.base_dir, args.output_dir, args.metadata_file)

    segment_audio(audio_path, json_path, output_dir, metadata_output_file, args.filename_base)


if __name__ == "__main__":
    main()