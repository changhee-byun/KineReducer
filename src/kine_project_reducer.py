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
    files = pathlib.Path(path).iterdir()
    mimetypes.init()
    resources = []
    for file in files:
        mimestart = mimetypes.guess_type(file)[0]
        if mimestart != None:
            mimestart = mimestart.split('/')[0]
            #if mimestart in ['audio', 'video', 'image']:
            if mimestart in [filter]:
                print(file)
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
        output_dir = pathlib.Path().absolute() / 'output_reducer'
        os.makedirs(output_dir, exist_ok=True)
    except:
        print(traceback.format_exc())
        sys.exit()

    args = sys.argv[1:]
    print(args)

    # args = ['/Users/CHANGHEE2/Projects/temp/kine/test']
    # args = ['./samples/20210603-4.kine']
    # args = ['/Users/CHANGHEE2/Projects/MES/KineReducer/samples/20210603-4.kine']
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
            print(index)
            print(traceback.format_exc())
        else:
            print("end of program")
        
    

# if __name__ == '__main__':

ffprobe_path = pathlib.Path(__file__).parent.absolute() / 'pre-ffmpeg' / 'ffprobe'
pre_ffmepg_bin = str(pathlib.Path(__file__).parent.absolute() / 'pre-ffmpeg')

os.system('echo $PATH')
os.environ["PATH"] += os.pathsep + pre_ffmepg_bin
print("-------")
os.system('echo $PATH')

# os.system("xattr -d com.apple.quarantine "+str(ffprobe_path))
# env = os.environ.copy()
# env['PATH'] = "{}{}{}".format(pre_ffmepg_bin, os.pathsep, env['PATH'])

# old_path = os.environ['PATH']
# try:
#     os.environ['PATH'] = "{}{}{}".format(pre_ffmepg_bin, os.pathsep, old_path)
#     print("correct")
# finally:
#     os.environ['PATH'] = old_path
    
run()

# # working directory
# print(pathlib.Path().absolute())

# # script file directory
# print(pathlib.Path(__file__).parent.absolute() / 'pre-ffmpeg')
# print("--------------------")





# os.system('echo $PATH')
# print("-------------")
# print("-------------")
# os.system('export PATH=$PATH:'+pre_ffmepg_bin)
# os.system('echo $PATH')
# os.system('ffprobe')
# os.system(ffprobe_path)