"""
This script:
    1) searches for pictures
    2) gets the year and month of each picture from meta-data
    3) creates dictionary with the data
    4) creates the tree directories to organize per year per month
    5) copies the pictures where they belong
"""
import os
import glob
import shutil
import time
import pathlib

from datetime import datetime

import toml

from PIL import Image
import organize_pics as ogpic

import time

import platform
from loguru import logger
import ffmpeg
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    datetime = pathlib.Path(path_to_file).stat().st_mtime
    logger.debug("datetime vid:", datetime)
    # datetime = datetime.replace(":", "_").replace(" ", "_")
    # logger.debug("datetime vid out:", datetime)
    return datetime

    # value = get_video_datetime_hachoir(path_to_file)
    # logger.debug("datetime vid:", value)
    # return get_video_datetime_hachoir(path_to_file)
    # return get_video_datetime_ffmpeg(path_to_file)
    # if platform.system() == 'Windows':
    #     return os.path.getctime(path_to_file)
    # else:
    #     stat = os.stat(path_to_file)
    #     try:
    #         return stat.st_birthtime
    #     except AttributeError:
    #         # We're probably on Linux. No easy way to get creation dates here,
    #         # so we'll settle for when its content was last modified.
    #         return stat.st_mtime


def get_video_datetime_ffmpeg(video_path):
    """
    Extracts the recording date and time from a video file using FFmpeg.
    
    :param video_path: Path to the video file.
    :return: Recording datetime as a string or None if not found.
    """
    try:
        # Use ffmpeg.probe to get metadata of the video
        probe = ffmpeg.probe(video_path, v='error', select_streams='v:0', show_entries='format_tags=creation_time')
        
        # Get the creation time from the metadata
        creation_time = probe.get('format', {}).get('tags', {}).get('creation_time', None)

        if creation_time:
            return creation_time
        else:
            print("No datetime metadata found.")
            return None
        
    except ffmpeg.Error as e:
        print(f"Error extracting metadata: {e}")
        return None
    

def get_video_datetime_hachoir(video_path):
    """
    Extracts the recording date and time from a video file using hachoir.
    
    :param video_path: Path to the video file.
    :return: Recording datetime as a string or None if not found.
    """
    parser = createParser(video_path)
    if not parser:
        print("Unable to parse file.")
        return None

    metadata = extractMetadata(parser)
    if not metadata:
        print("No metadata found.")
        return None

    # Extract creation date if available
    return metadata.get("creation_date")

def get_videos(path_src):
    """
    Get a list of all the files corresponding to the defined extensions
    :param path_src: path to directory containing the unsorted pictures
    :return: list of all corresponding files
    """
    vid_ext = ['*.mp4', '*.3gp', '*.MOV', '*.MTS']
    # vid_ext = ['mp4']

    # out = []
    # logger.info("\t\t> Search images in \t %s" % path_src)
    # for ext in vid_ext:
    #     logger.info("\t\t> ext: %s" % ext)
    #     files = glob.iglob("%s/**/*.%s" % (path_src, ext.upper()), recursive=True)
    #     for file in files:
    #         out.append(file)

    #     files = glob.iglob("%s/**/*.%s" % (path_src, ext.lower()), recursive=True)
    #     for file in files:
    #         out.append(file)

    # return out

    file_list = ogpic.get_files_list_recursively_enabling_links(path_src, vid_ext)
    logger.info(" > found %d videos" % len(file_list))
    return file_list


def copy_videos(my_videos, in_path, out_path, remove_file=False):
    # todo: YYYY_MM_DD_name format
    for video in my_videos:
        _, file_name = os.path.split(video)
        # creation_time =  time.ctime(os.path.getctime(video))
        creation_time =  time.ctime(creation_date(video))
        date_time = datetime.strptime(creation_time, "%a %b %d %H:%M:%S %Y")
        prefix = "%04d_%02d_%02d" % (date_time.year, date_time.month, date_time.day)
        out_full_name = os.path.join(out_path, "%s_%s" % (prefix, file_name))
        if os.path.isfile(out_full_name):
            logger.info(' > No copy of "%s" to "%s" (already exists)' % (video, out_full_name))
            if remove_file:
                os.remove(video)
        else:
            if remove_file:
                logger.info(' > Move "%s" to "%s"' % (video, out_full_name))
                os.rename(video, out_full_name)
            # shutil.copyfile(video, out_full_name)

    # for file, subtree in copy_dict.items():
    #     filename = file.split('/')[-1]
    #     full_out_path = os.path.join(out_path, subtree, filename)
    #     if os.path.isfile(full_out_path):
    #         logger.info(' > No copy of "%s" to "%s" (already exists)' % (file, os.path.join(out_path, subtree, filename)))
    #     else:
    #         logger.info(' > Copy "%s" to "%s"' % (file, os.path.join(out_path, subtree, filename)))
    #         shutil.copyfile(file, os.path.join(out_path, subtree, filename))
    #     if remove_file:
    #         os.remove(file)


def main(in_path, out_path):
    """
    Main routine that calls all the other ones
    :param in_path: path to input folder containing the unsorted pictures
    :param out_path: path to output folder that will contain the sorted pictures
    """

    logger.info("\t> Find files")
    my_videos = get_videos(in_path)

    logger.info("\t> Create output folder if missing")
    ogpic.create_folders('', [out_path]) 
 
    logger.info("\t> Copy and cleanup")
    copy_videos(my_videos, in_path, out_path, remove_file=True)

    ogpic.clean_empty_directories(in_path)


if __name__ == "__main__":
    # TODO: there is a mistake in the years! 2019 instead of 2020! (Only on reflex...)

    # time loop is handled via crontab
    params = toml.load('./config.toml')
    logger.info(" > %s --> Sort Videos" % ogpic.get_time())
    main(params['Sort']['input_dir'], params['Videos']['video_dir'])
    logger.info(" > Done.")
