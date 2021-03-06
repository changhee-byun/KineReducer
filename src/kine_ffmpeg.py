# brew install ffmpeg
# pip install ffmpeg-python

import ffmpeg
import os
from kine_logger import KineLogger
from pathlib import Path
import math

def re_encode_video(input_path, output_path, width, height, rotate):
    overwrite = False
    if input_path == output_path:
        output_path = str(Path(output_path).parent / "temp.mp4")
        overwrite = True
    input_stream = ffmpeg.input(input_path)
    # ffmpeg.nodes.get_stream_spec_nodes(input_stream)[0].kwargs['noautorotate'] = ''

    video_stream_filter = input_stream.video

    # transpos parameter
    # 0 = 90CounterCLockwise and Vertical Flip (default)
    # 1 = 90Clockwise
    # 2 = 90CounterClockwise
    # 3 = 90Clockwise and Vertical Flip

    # if a video is rotated, revers-rotate it before scaling media size.
    if rotate == 90 :
        video_stream_filter = ffmpeg.filter(video_stream_filter, 'transpose', 2)
    elif abs(rotate) == 180 :
        video_stream_filter = ffmpeg.filter(video_stream_filter, 'transpose', 2)
        video_stream_filter = ffmpeg.filter(video_stream_filter, 'transpose', 2)
    elif rotate == 270 :
        video_stream_filter = ffmpeg.filter(video_stream_filter, 'transpose', 1)

    video_stream_filter = ffmpeg.filter(video_stream_filter, 'scale', width, height)
    
    has_audio = ffmpeg.probe(input_path, select_streams='a')

    if has_10_bit_depth(input_path):
        # default codec ID(vtag) is 'hev1' by x265. But 'hev1' is not playable on iOS and MacOS.
        # we need to change the vtag to 'hvc1' from 'hev1'.
        args = {'vcodec':'libx265', 'vtag':'hvc1'} 
    else:
        args = {}

    if has_audio['streams']:
        # input_stream = ffmpeg.output(video_stream_filter, input_stream.audio, output_path, vcodec='libx265')
        input_stream = ffmpeg.output(video_stream_filter, input_stream.audio, output_path, **args)
    else:
        input_stream = ffmpeg.output(video_stream_filter, output_path, **args)

    ffmpeg.run(input_stream)

    if rotate != 0:
        write_rotate_metadata(output_path, output_path, rotate)
    
    if overwrite == True:
        os.remove(input_path)
        output_path = Path(output_path).rename(input_path)

def write_rotate_metadata(input_path, output_path, rotation):
    overwrite = False
    if input_path == output_path:
        output_path = str(Path(output_path).parent / "temp_rotate.mp4")
        overwrite = True

    ## Possible rotation metadata in video are 0, 90, 180, 270.
    ## I don't fully understand, but we need to add 180 to write the rotation data we want.     
    # metadata_rotate = str(180 + rotation) ## keep original rotation.

    ## match preview screen and timeline thumbnail.
    ## 90->90, 180->180, 270->90. (270 is highly likely to be incorrect rotation.)
    metadata_rotate = str(180 + rotation) if rotation <= 90 else str(rotation)
    (
        ffmpeg.input(input_path)
        .output(output_path, vcodec='copy', acodec='copy', **{'metadata:s:v': 'rotate='+metadata_rotate})
        .run()
    )

    if overwrite == True:
        os.remove(input_path)
        output_path = Path(output_path).rename(input_path)
    


def re_encode_video_fluent(input_path, output_path, width, height, rotate):
    overwrite = False
    if input_path == output_path:
        output_path = str(Path(output_path).parent / "temp.mp4")
        overwrite = True

    has_audio = ffmpeg.probe(input_path, select_streams='a')
    input_stream = ffmpeg.input(input_path)
    if rotate == 90 :
        transpos_value = 2
    elif abs(rotate) == 180 :
        transpos_value = 3
    elif rotate == 270 :
        transpos_value = 2
    else :
        transpos_value = 0

    output_path_temp = str(Path(output_path).parent / "temp_temp.mp4")

    if has_audio['streams']:
        (
            ffmpeg.input(input_path)
            # .filter('transpose', transpos_value)
            # .filter('scale', height, width)
            .filter('scale', width, height)
            .filter('transpose', 1)

            # .output(output_path, metadata='title=TestTitle')
            # .output(output_path, **{'metadata':'title=TestTitle2'})
            # .output(output_path_temp, **{'metadata:s:v':'rotate=270'})
            # .output(output_path_temp)
            
            # .output(output_path, **{'metadata:s:v:0': 'rotate=270'})
            # .filter('rotate', float(rotate)*(math.pi/180.0))
             .output(input_stream.audio, output_path_temp)
            #  .output(input_stream.audio, output_path)
            # .output(input_stream.audio, output_path, map_metadata=0)
            # .output(input_stream.audio, output_path, **{'metadata:s:v:0': 'rotate="270"'})
            # .output(input_stream.audio, output_path, **{'map_metadata':0})
            .run()
        )

        (
            ffmpeg.input(output_path_temp)
            .output(output_path, vcodec='copy', acodec='copy', **{'metadata:s:v': 'rotate=450'})
            .run()
        )
        
    else :
        (
            # ffmpeg.input(input_path)
            # .filter('scale', width, height)
            # .output(output_path, map_metadata=0)
            # .run()
        )
    
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
    print(video_stream)
    try :
        rotate = video_stream['tags']['rotate']
    except :
        rotate = 0
    return video_stream['width'], video_stream['height'], rotate

def has_10_bit_depth(path):
    video_stream = ffmpeg.probe(path, select_streams = "v")['streams'][0]

    # trying to print a bit depth. it's not working.
    # args = {"loglevel": "panic",
    #         "show_entries": "stream=bits_per_raw_sample",
    #         "select_streams": "v",
    #         }
    # print(ffmpeg.probe(path , **args))
    

    # For bit-depth=8 of libx264 it will be something like:
    #     Supported pixel formats: yuv420p yuvj420p yuv422p yuvj422p yuv444p yuvj444p nv12 nv16
    # And for bit-depth=10 of libx264 it will be something like:
    #     Supported pixel formats: yuv420p10le yuv422p10le yuv444p10le nv20le

    bit_depth_8_support_pix_fmt =  ['yuv420p', 'yuvj420p', 'yuv422p', 'yuvj422p', 'yuv444p', 'yuvj444p', 'nv12', 'nv16']
    bit_depth_10_support_pix_fmt = ['yuv420p10le', 'yuv422p10le', 'yuv444p10le', 'nv20le']
    
    support_10_bit = False

    try :
        if video_stream['pix_fmt'] in bit_depth_10_support_pix_fmt:
            support_10_bit = True
    except :
        support_10_bit = False

    return support_10_bit
