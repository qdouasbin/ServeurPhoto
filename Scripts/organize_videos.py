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

from datetime import datetime

import toml

from PIL import Image
import organize_pics as ogpic

import time

import platform

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime



def get_videos(path_src):
    """
    Get a list of all the files corresponding to the defined extensions
    :param path_src: path to directory containing the unsorted pictures
    :return: list of all corresponding files
    """
    vid_ext = ['mp4', '3gp', 'MOV', 'MTS']
    # vid_ext = ['mp4']

    out = []
    print("\t\t> Search images in \t %s" % path_src)
    for ext in vid_ext:
        print("\t\t> ext: %s" % ext)
        files = glob.iglob("%s/**/*.%s" % (path_src, ext.upper()), recursive=True)
        for file in files:
            out.append(file)

        files = glob.iglob("%s/**/*.%s" % (path_src, ext.lower()), recursive=True)
        for file in files:
            out.append(file)

    return out


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
            print(' > No copy of "%s" to "%s" (already exists)' % (video, out_full_name))
            if remove_file:
                os.remove(video)
        else:
            if remove_file:
                print(' > Move "%s" to "%s"' % (video, out_full_name))
                os.rename(video, out_full_name)
            # shutil.copyfile(video, out_full_name)

    # for file, subtree in copy_dict.items():
    #     filename = file.split('/')[-1]
    #     full_out_path = os.path.join(out_path, subtree, filename)
    #     if os.path.isfile(full_out_path):
    #         print(' > No copy of "%s" to "%s" (already exists)' % (file, os.path.join(out_path, subtree, filename)))
    #     else:
    #         print(' > Copy "%s" to "%s"' % (file, os.path.join(out_path, subtree, filename)))
    #         shutil.copyfile(file, os.path.join(out_path, subtree, filename))
    #     if remove_file:
    #         os.remove(file)


def main(in_path, out_path):
    """
    Main routine that calls all the other ones
    :param in_path: path to input folder containing the unsorted pictures
    :param out_path: path to output folder that will contain the sorted pictures
    """

    print("\t> Find files")
    my_videos = get_videos(in_path)

    print("\t> Copy and cleanup")
    copy_videos(my_videos, in_path, out_path, remove_file=True)

    ogpic.clean_empty_directories(in_path)


if __name__ == "__main__":
    # TODO: there is a mistake in the years! 2019 instead of 2020! (Only on reflex...)

    # time loop is handled via crontab
    params = toml.load('./config.toml')
    print(" > %s --> Sort Videos" % ogpic.get_time())
    main(params['Sort']['input_dir'], params['Videos']['video_dir'])
    print(" > Done.")
