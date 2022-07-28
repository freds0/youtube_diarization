# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (C) 2021 Frederico Oliveira fred.santos.oliveira(at)gmail.com
#
#
import argparse
import sys
from os import makedirs
from os.path import join, exists, split
import time
import youtube_dl
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from random import randint


def my_progress(d):
    '''
    Show download progress.
    '''
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def download_from_youtube(yt_url, output_path, video_download = False, transcript_download = False): # function for ingesting when given a url
    '''
    Download audio and subtitle from a youtube video given a url.
        Parameters:
        yt_url (str): Youtube URL format https://www.youtube.com/watch?v=XXXXXXXXXXX
        output_path (str): folder to save youtube audio.
        video_download (Boolean): True for downloading video mp4.
        transcript_download (Boolean): True for transcription from youtube.

        Returns:
        String: returns True or False

    '''
    # Use vid as the diretory name for download and processing
    vids = parse_qs(urlparse(yt_url).query, keep_blank_values=True).get('v')
    vid = None if vids == None else vids[0]

    video_dir = join(output_path, str(vid).strip())

    # Filename for audio stream (.mp4) and subtitle (.srt) files
    audio_filename = join(video_dir, vid.strip() + '.tmp')
    video_filename = join(video_dir, vid.strip() + '.mp4')
    subtitle = join(video_dir, vid + '.srt')

    if Path(video_filename).exists() and Path(subtitle).exists():
        return False

    #if exists(audio.replace('.webm', '.mp3')) and exists(subtitle):
    #    return False

    # Get information on the YouTube content
    try:
        # Random time do waiting to avoid youtube access blocking
        t = randint(30,60)
        print('Waiting %d seconds ...'%(t))
        time.sleep(t) # Overcome YouTube blocking

        if not (exists(video_dir)):
            makedirs(video_dir)

        #####################################################################################
        # Download Audio
        #####################################################################################
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': audio_filename,        
            'noplaylist' : True,        
            'progress_hooks': [my_progress],  
        }
        # Download audio stream and convert to mp3
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_url])


        #####################################################################################
        # Download Video
        #####################################################################################
        if video_download:

            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',      
                'outtmpl': video_filename,        
                'noplaylist' : True,        
                'progress_hooks': [my_progress]
            }
            # Download audio stream and convert to mp3
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([yt_url])

        #####################################################################################
        # Download Transcript
        #####################################################################################
        if transcript_download:
            # get video_id from youtube_uri
            video_id = yt_url.replace('https://www.youtube.com/watch?v=','')
            # Download subtitle and write to an .srt file
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            '''
            # filter first for manually created transcripts and second for automatically generated ones
            transcript = transcript_list.find_transcript(['en'])
            # get only text from transcript
            text_transcript_list = []
            for line in transcript.fetch():
                text_transcript_list.append(line['text'])
            text_transcript = ' '.join(text_transcript_list)
            '''
            # filter for manually created transcripts
            transcript = transcript_list.find_manually_created_transcript(['pt'])
            text_transcript_list = []
            for line in transcript.fetch():
                text_transcript_list.append(line['text'])
            text_transcript = ' '.join(text_transcript_list)

            #####################################################################################
            # Write transcript to file
            #####################################################################################
            output_file = open(join(video_dir, vid.strip() + '.srt'), 'w')
            output_file.write(text_transcript)
            output_file.close()

    except KeyboardInterrupt:
        print("KeyboardInterrupt Detected!")
        exit()

    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        exc_file = split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, exc_file, exc_tb.tb_lineno)
        return False

    return audio_filename.replace('.tmp', '.mp3')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', default='links.txt', help="Input txt file.")
    #parser.add_argument('--youtube_url', help="URL of the youtube video.")
    parser.add_argument('--output_dir', default='videos', help='Directory to save downloaded audio and transcript files.')

    args = parser.parse_args()

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

        #else:
        #    print("URL of the video file should start with https://")
        #    sys.exit(1)


if __name__ == '__main__':
    main()

