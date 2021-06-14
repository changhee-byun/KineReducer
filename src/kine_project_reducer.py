import kine_zip as zip
import kine_ffmpeg as ffmpeg
import sys
import traceback
import os
import pathlib
from pathlib import Path
import mimetypes
import shutil
from PIL import Image
from kine_logger import KineLogger
from datetime import datetime


def print_usage():
    print("Usage----")

def read_kine_files(args):
    kine_files = []
    if len(args) == 0:
        for user_input_path in pathlib.Path().iterdir():
            if user_input_path.suffix == '.kine':
                kine_files.append(user_input_path)
    elif len(args) >= 1:
        for arg in args:
            # if os.path.isdir(arg):
            if pathlib.Path(arg).is_dir():
                for user_input_path in pathlib.Path(arg).iterdir():
                    if user_input_path.suffix == '.kine':
                        kine_files.append(user_input_path)
            else:
                kine_files.append(arg)
                    
    else:
        print_usage()

    return kine_files

def get_resources(path, filter):
    KineLogger.debug("get resouces")
    files = pathlib.Path(path).iterdir()
    mimetypes.init()
    resources = []
    for file in files:
        mimestart = mimetypes.guess_type(file)[0]
        if mimestart != None:
            mimestart = mimestart.split('/')[0]
            #if mimestart in ['audio', 'video', 'image']:
            if mimestart in [filter]:
                KineLogger.info(file)
                resources.append(file)

    return resources

def delete(path):
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            os.remove(path)

def resize_videos(video_resources):
    # reduce video resource size
    for video in video_resources:
        width, height = ffmpeg.get_video_resolution(video)
        ratio = min(width / 480.0, height / 480.0)
        if ratio > 1.0:
            # output = copy.deepcopy(video)
            resize_width = (width / ratio) if (width / ratio)%2 == 0 else (width / ratio) + 1
            resize_height = (height / ratio) if (height / ratio)%2 == 0 else (height / ratio) + 1

            ffmpeg.re_encode_video(str(video), str(video), resize_width, resize_height)

def resize_images(image_resources):
    for image_path in image_resources:
        image = Image.open(image_path)
        width, height = image.size
        ratio = min(width / 720.0, height / 720.0)
        if ratio > 1.0:
            title, ext = os.path.splitext(image_path)
            img_resize = image.resize((int(image.width / ratio), int(image.height / ratio)))
            delete(image_path)
            img_resize.save(image_path)

def run():
    try :
        now = datetime.now()
        datetime_string = now.strftime("%y%m%d-%H_%M_%S")
        output_dir = pathlib.Path().absolute() / 'output_reducer' / datetime_string
        os.makedirs(output_dir, exist_ok=True)
        logfile_name = 'log_' + datetime_string + '.txt'
        logfile = output_dir / logfile_name

        KineLogger.set_logfile(str(logfile))
    except:
        print(traceback.format_exc())
        sys.exit()

    args = sys.argv[1:]
    print(args)

    # args = ['/Users/CHANGHEE2/Projects/temp/kine/test']
    # args = ['./samples/20210603-4.kine']
    # args = ['/Users/CHANGHEE2/Projects/MES/KineReducer/samples/20210603-4.kine']
    # args = ['./samples/20210603-6.kine']
    kine_files = read_kine_files(args)

    if kine_files.count == 0:
        print_usage()
        sys.exit()

    for index, kine_file in enumerate(kine_files):
        try:
            # unzip kinefile
            file_name = Path(kine_file).stem
            dest_path = output_dir / file_name
            delete(dest_path)
            zip.unzip(kine_file, dest_path)
            contents_dir = dest_path / 'contents'

            # get video resource path list
            video_resources = get_resources(contents_dir, 'video')
            if len(video_resources) > 0:
                resize_videos(video_resources)

            # get image resouce path list
            image_resouces = get_resources(contents_dir, 'image')
            if len(image_resouces) > 0:
                resize_images(image_resouces)

            # zip dir
            zip.zip_dir(dest_path, output_dir, Path(kine_file).name)
            delete(dest_path)

        except:
            # http://docs.python.org/2/library/sys.html#sys.exc_info
            KineLogger.error('file index - ' + str(index))
            KineLogger.error(traceback.format_exc())
        else:
            KineLogger.info("---- Done ----")
        
    

# if __name__ == '__main__':

# # working directory
# print(pathlib.Path().absolute())

# # script file directory
# print(pathlib.Path(__file__).parent.absolute() / 'pre-ffmpeg')




# # ffprobe_path = pathlib.Path(__file__).parent.absolute() / 'pre-ffmpeg' / 'ffprobe'
# pre_ffmepg_bin = str(pathlib.Path(__file__).parent.absolute() / 'pre-ffmpeg')
# os.environ["PATH"] += os.pathsep + pre_ffmepg_bin
# # os.system('echo $PATH')
    
run()



