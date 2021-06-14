import kine_zip as zip

import sys
import traceback
import os
from pathlib import Path
from kine_logger import KineLogger
from datetime import datetime
import kine_file_util as fileutil
import kine_media_resizer as resizer

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

    args = sys.argv[1:]
    print(args)

    # args = ['/Users/CHANGHEE2/Projects/temp/kine/test']
    # args = ['./samples/20210603-4.kine']
    # args = ['/Users/CHANGHEE2/Projects/MES/KineReducer/samples/20210603-4.kine']
    # args = ['./samples/20210603-6.kine']
    kine_files = fileutil.read_kine_files(args)

    if kine_files.count == 0:
        KineLogger.print_usage()
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
                resizer.resize_videos(video_resources)

            # get image resouce path list
            image_resouces = fileutil.get_resources(contents_dir, 'image')
            if len(image_resouces) > 0:
                resizer.resize_images(image_resouces)

            # zip dir
            zip.zip_dir(dest_path, output_dir, Path(kine_file).name)
            fileutil.delete(dest_path)

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



