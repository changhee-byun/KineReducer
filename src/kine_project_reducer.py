import kine_zip as zip

import sys
import traceback
import os
from pathlib import Path
from kine_logger import KineLogger
from datetime import datetime
import kine_file_util as fileutil
import kine_media_resizer as resizer
import argparse

__VERSION__ = '1.0.0'

def run():
    try :
        now = datetime.now()
        datetime_string = now.strftime("%y%m%d-%H_%M_%S")
        output_dir = Path().absolute() / 'output_reducer' / datetime_string
        os.makedirs(output_dir, exist_ok=True)
        logfile_name = 'log_' + datetime_string + '.txt'
        logfile = output_dir / logfile_name

        KineLogger.set_logfile(str(logfile))
    except:
        print(traceback.format_exc())
        sys.exit()

    # args = sys.argv[1:]
    # print(args)
    parser = get_parser()
    args = parser.parse_args()

    kine_files = fileutil.read_kine_files(args.path)

    if len(kine_files) == 0:
        parser.print_help()
        sys.exit()

    for index, kine_file in enumerate(kine_files):
        try:
            # unzip kinefile
            file_name = Path(kine_file).stem
            dest_path = output_dir / file_name
            fileutil.delete(dest_path)
            zip.unzip(kine_file, dest_path)
            contents_dir = dest_path / 'contents'

            # get video resource path list
            video_resources = fileutil.get_resources(contents_dir, 'video')
            if len(video_resources) > 0:
                resizer.resize_videos(video_resources, args.video_resolution)

            # get image resouce path list
            image_resouces = fileutil.get_resources(contents_dir, 'image')
            if len(image_resouces) > 0:
                resizer.resize_images(image_resouces, args.image_resolution)

            # zip dir
            zip.zip_dir(dest_path, output_dir, Path(kine_file).name)
            fileutil.delete(dest_path)

        except:
            # http://docs.python.org/2/library/sys.html#sys.exc_info
            KineLogger.error('file index - ' + str(index))
            KineLogger.error(traceback.format_exc())
            fileutil.delete(dest_path)
        else:
            KineLogger.info("---- Done ----")
        
def get_parser():
    parser = argparse.ArgumentParser(description='Reduce KineMaster project file size.', prog='kine_project_reducer')
    parser.add_argument('path', metavar='project file or folder path', type=str, nargs='+',
                        help='a path to .kine file(s) or foler containing .kine file(s).')
    parser.add_argument('-i', '--image', dest='image_resolution', action='store', default=720,
                        help='the image resolution to encode. (default: 720)')
    parser.add_argument('-v', '--video', dest='video_resolution', action='store', default=480,
                        help='the video resolution to encode. (default: 480)')
    parser.add_argument('-version', '--version', action='version', version='%(prog)s {}'.format(__VERSION__))

    return parser


if __name__ == '__main__':
    # add a ffmpeg path to the system environment path.
    pre_ffmepg_bin = str(Path(__file__).parent.absolute() / 'pre-ffmpeg')
    os.environ["PATH"] += os.pathsep + pre_ffmepg_bin
    # os.system('echo $PATH')
    
    run()


# # working directory
# print(pathlib.Path().absolute())

# # script file directory
# print(pathlib.Path(__file__).parent.absolute() / 'pre-ffmpeg')

