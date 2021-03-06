import kine_zip as zip
import sys
import traceback
import os
from pathlib import Path
from kine_logger import KineLogger
from datetime import datetime
import kine_file_util as fileutil
import kine_media_resizer as resizer
import kine_protobuf as kinejson
import argparse
from kine_info import __VERSION__
from kine_info import *

def run(parser):
    try :
        now = datetime.now()
        datetime_string = now.strftime("%y%m%d-%H_%M_%S")
        output_dir = Path().absolute() / OUTPUT_FOLDER / datetime_string
        os.makedirs(output_dir, exist_ok=True)
        json_dir = output_dir / "json"
        os.makedirs(json_dir, exist_ok=True)
        project_json_dir = json_dir / "project"
        os.makedirs(project_json_dir, exist_ok=True)
        pds_info_json_dir = json_dir / "PDS_info"
        os.makedirs(pds_info_json_dir, exist_ok=True)

        logfile_name = 'log_' + datetime_string + '.txt'
        logfile = output_dir / logfile_name
        KineLogger.set_logfile(str(logfile), LOGGING_NAME)
    except:
        print(traceback.format_exc())
        sys.exit()
    
    KineLogger.info('[ KineReducer v{} ]'.format(__VERSION__))
    KineLogger.info('Output folder -> ' + str(output_dir))
    
    # args = sys.argv[1:]
    # print(args)
    # parser = get_parser()
    args = parser.parse_args()

    kine_files = fileutil.read_kine_files(args.path)
    file_count = len(kine_files)

    if file_count == 0:
        KineLogger.error("Invalid path")
        parser.print_help()
        sys.exit()

    KineLogger.info('------------------------------------')
    KineLogger.info('------ file(s) to be reduced -------')
    for index, kine_file in enumerate(kine_files):        
        KineLogger.info('{}. {}'.format(index+1, str(kine_file)))
    KineLogger.info('------------------------------------')
    KineLogger.info('------------------------------------')

    json_only_mode = str(args.json_only).lower() in ['true', '1', 't', 'y', 'yes']

    if json_only_mode:
        KineLogger.info('')
        KineLogger.info('>>>>>>>>>> Generating JSON Only (No Resizing) <<<<<<<<<<')
        KineLogger.info('')

    results = []
    for index, kine_file in enumerate(kine_files):
        try:
            KineLogger.info('---------({}/{}) current file : [{}]'.format(index+1, file_count, str(kine_file)))

            # unzip kinefile
            file_name = Path(kine_file).stem
            dest_path = output_dir / file_name
            fileutil.delete(dest_path)
            zip.unzip(kine_file, dest_path)
            contents_dir = dest_path / CONTENTS

            if not json_only_mode:
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

                reduced_file = os.path.relpath(str(output_dir / Path(kine_file).name), Path().parent.absolute())
                results.append(('{}. {}'.format(index+1, str(kine_file)), True, reduced_file))

            # get kmproj file
            kmproject_file_path = fileutil.get_kmproj_file(dest_path)
            kinejson.km_protobuf_to_json(kmproject_file_path, project_json_dir, file_name, str(args.print_json).lower() in ['true', '1', 't', 'y', 'yes'])
            kinejson.km_protobuf_to_PDS_info(kmproject_file_path, pds_info_json_dir, "{}(PDS)".format(file_name), str(args.print_json).lower() in ['true', '1', 't', 'y', 'yes'])

            if json_only_mode:
                json_file = os.path.relpath(str(project_json_dir / Path(file_name).name), Path().parent.absolute())
                results.append(('{}. {}'.format(index+1, str(kine_file)), True, "{}.json".format(json_file)))

            fileutil.delete(dest_path)

        except:
            # http://docs.python.org/2/library/sys.html#sys.exc_info
            KineLogger.error('Failed to reduced the file [{}. {}]'.format(index+1, str(kine_file)))
            KineLogger.error(traceback.format_exc())
            fileutil.delete(dest_path)
            results.append(('{}. {}'.format(index+1, str(kine_file)), False, 'None'))
        else:
            KineLogger.info('---------({}/{}) Resizing the file is done. [{}]'.format(index+1, file_count, str(kine_file)))

    KineLogger.info('------------------------------------')
    KineLogger.info('----------- Work results ------------')
    KineLogger.info('| File | Result | Reduced file |')

    summary = []
    for result in results:
        success = 'Success' if result[1] == True else 'Fail'
        summary.append(success)
        KineLogger.info('| {} | {} | {} |'.format(result[0], success, result[2]))
    
    success_count = summary.count('Success')
    fail_count = summary.count('Fail')
    KineLogger.info('|')
    KineLogger.info('| ->  Success: {} file(s) / Fail: {} file(s)'.format(success_count, fail_count))
    KineLogger.info('------------------------------------')


        
def get_parser():
    parser = argparse.ArgumentParser(description='Reduce KineMaster project file size.', prog='KineReducer')
    parser.add_argument('path', metavar='project file or folder path', type=str, nargs='+',
                        help='a path to .kine file(s) or foler(s) containing .kine file(s).')
    parser.add_argument('-is', '--image-scale', dest='image_resolution', action='store', default=720,
                        help='set the output image resolution with original aspect ratio. (default: 720)')
    parser.add_argument('-vs', '--video-scale', dest='video_resolution', action='store', default=480,
                        help='set the output video resolution with original aspect ratio. (default: 480)')
    parser.add_argument('-jo', '--json-only', dest='json_only', action='store', default='no',
                        help='generate project json document(s) without project resizing. it could be \'yes\', \'y\' or \'false\' (default: no)')
    parser.add_argument('-pj', '--print-json', dest='print_json', action='store', default='no',
                        help='print json string on the screen while KineReducer processing. it could be \'yes\', \'y\' or \'false\' (default: no)')
    parser.add_argument('-version', '--version', action='version', version='%(prog)s {}'.format(__VERSION__))

    return parser


if __name__ == '__main__':
    parser = get_parser()
    parser.parse_args()

    # add a ffmpeg path to the system environment path.
    pre_ffmepg_bin = str(Path(__file__).parent.absolute() / FFMPEG_FOLDER)
    os.environ["PATH"] += os.pathsep + pre_ffmepg_bin
    # os.system('echo $PATH')
    
    run(parser)


# # working directory
# print(pathlib.Path().absolute())

# # script file directory
# print(pathlib.Path(__file__).parent.absolute() / 'pre-ffmpeg')

