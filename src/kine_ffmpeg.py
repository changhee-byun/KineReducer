# brew install ffmpeg
# pip install ffmpeg-python

import ffmpeg
import os
from kine_logger import KineLogger
from pathlib import Path


def re_encode_video(input_path, output_path, width, height):
    overwrite = False
    if input_path == output_path:
        output_path = str(Path(output_path).parent / "temp.mp4")
        overwrite = True
    input_stream = ffmpeg.input(input_path)
    video_stream_scaled = ffmpeg.filter(input_stream.video, 'scale', width, height)
    input_stream = ffmpeg.output(video_stream_scaled, input_stream.audio, output_path)
    ffmpeg.run(input_stream)
    
    if overwrite == True:
        os.remove(input_path)
        output_path = Path(output_path).rename(input_path)

# def get_video_resolution(path):
#     # video_streams = ffmpeg.probe(path, select_streams = "v")
#     probe = ffmpeg.probe(path)
#     video_streams = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
#     height = video_streams[0]['height']
#     return height


def get_video_resolution(path):
    print(path)
    video_stream = ffmpeg.probe(path, select_streams = "v")['streams'][0]
    return video_stream['width'], video_stream['height']
