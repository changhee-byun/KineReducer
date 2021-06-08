import kine_zip as zip
import kine_ffmpeg as ffmpeg
import sys
import traceback
import os
import pathlib
from pathlib import Path
import mimetypes
import shutil

def print_usage():
    print("Usage----")

def get_kine_files():
    return ['/Users/CHANGHEE2/Projects/temp/kine/20210603-2.kine']

def run_reducer(kine_files):
    print("main process")

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

def get_video_resources(path):
    files = pathlib.Path(path).iterdir()
    mimetypes.init()
    video_resources = []
    for file in files:
        mimestart = mimetypes.guess_type(file)[0]
        if mimestart != None:
            mimestart = mimestart.split('/')[0]
            #if mimestart in ['audio', 'video', 'image']:
            if mimestart in ['video']:
                print(file)
                video_resources.append(file)

    return video_resources


# if __name__ == '__main__':
try :
    output_dir = pathlib.Path().absolute() / 'output_reducer'
    os.makedirs(output_dir, exist_ok=True)
except:
    print(traceback.format_exc())
    sys.exit()

args = sys.argv[1:]
print(args)

# args = ['/Users/CHANGHEE2/Projects/temp/kine/test']
args = ['./samples']
kine_files = read_kine_files(args)

if kine_files.count == 0:
    print_usage()
    sys.exit()

for index, kine_file in enumerate(kine_files):
    try:
        # unzip kinefile
        file_name = Path(kine_file).stem
        dest_path = output_dir / file_name
        if dest_path.exists() and dest_path.is_dir():
            shutil.rmtree(dest_path)
        zip.unzip(kine_file, dest_path)

        # get video resource path list
        video_resources = get_video_resources(dest_path / 'contents')
        if video_resources.count == 0:
            continue

        # reduce video resource size
        for video in video_resources:
            width, height = ffmpeg.get_video_resolution(video)
            if height > 480:
                # output = copy.deepcopy(video)
                ffmpeg.re_encode_video(str(video), str(video))         

        # zip dir
        zip.zip_dir(dest_path, output_dir, Path(kine_file).name)  
        if dest_path.exists() and dest_path.is_dir():
            shutil.rmtree(dest_path)
    except:
        # http://docs.python.org/2/library/sys.html#sys.exc_info
        print(index)
        print(traceback.format_exc())
    else:
        print("end of program")
        
    