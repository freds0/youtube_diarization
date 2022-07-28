# Youtube Diarization using pyannote-audio

This tools download audios from youtube and execute diarization by speaker using [pyannote-audio.](https://github.com/pyannote/pyannote-audio)

## Installation

This project has been tested on Ubuntu 20.04.4 LTS. First, you need to install the [FFmpeg](https://ffmpeg.org/) program using the following command:

```bash
$ sudo apt update; apt install ffmpeg
```


To create a conda environment from scratch, run the following commands

```bash
$ conda create -n youtube_diarization python=3.9 pip
```

Activate the environment:

```bash
$ conda activate youtube_diarization
```

Use the package manager pip to install the requirements.

First, install speechbrain (torch is a requirement):

```bash
$ conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 -c pytorch
$ pip install speechbrain
```

After, install pyannote-audio:

```bash
$ pip install https://github.com/pyannote/pyannote-audio/archive/develop.zip
```

Finally, install other requirements:

```bash
$ pip install -r requirements.txt
```

Or use the yml file:

```bash
$ conda env create -f environment.yml
```

## Configuration

Create a youtube links file, one link for line:

```bash
$ cat input/links.txt
```

Your file should look something like this:
```
# Yoshua Bengio interview
https://www.youtube.com/watch?v=Tzuhnuo8KQg
# Ian Goodfellow interview
https://www.youtube.com/watch?v=Z6rxFNMGdn0
# Andrew Ng interview
https://www.youtube.com/watch?v=0jspaMLxBig
# Geoffrey Hinton interview
https://www.youtube.com/watch?v=-eyhCTvrEtE
```

If the line starts with '#' it will be ignored. 

## Execution

For execution it is necessary to use a configuration file, such as the config.json file:

```
{
  "youtube_list": "input/links.txt", 
  "videos_folder": "output/videos"
}
```

- **youtube_list**: input filepath containing the youtube links.
- **videos_folder**: output folder in which downloaded audios/videos will be segmented.

To execution, run the command: 

```bash
$ python main.py -c config.json
```

## License

[Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0)
