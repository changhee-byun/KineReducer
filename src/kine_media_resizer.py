from kine_logger import KineLogger
import kine_ffmpeg as ffmpeg
from PIL import Image
import kine_file_util as fileutil
import os

def resize_videos(video_resources, resolution):
    # reduce video resource size
    for video in video_resources:
        width, height = ffmpeg.get_video_resolution(video)
        ratio = min(width / float(resolution), height / float(resolution))
        if ratio > 1.0:
            # output = copy.deepcopy(video)
            resize_width = (width / ratio) if (width / ratio)%2 == 0 else (width / ratio) + 1
            resize_height = (height / ratio) if (height / ratio)%2 == 0 else (height / ratio) + 1

            ffmpeg.re_encode_video(str(video), str(video), resize_width, resize_height)

def resize_images(image_resources, resolution):
    for image_path in image_resources:
        image = Image.open(image_path)
        width, height = image.size
        ratio = min(width / float(resolution), height / float(resolution))
        if ratio > 1.0:
            title, ext = os.path.splitext(image_path)
            img_resize = image.resize((int(image.width / ratio), int(image.height / ratio)))
            fileutil.delete(image_path)
            img_resize.save(image_path)