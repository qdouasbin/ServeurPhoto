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
from pathlib import Path

from datetime import datetime

import toml

from PIL import Image
from PIL.ExifTags import TAGS 

from loguru import logger


def get_files_list_recursively_enabling_links(root_dir, patterns):
    """
    Recursively finds files matching multiple patterns in a directory,
    following symbolic links as well.

    :param root_dir: The root directory to start searching from.
    :param patterns: A list of file patterns to match (e.g., ["*.txt", "*.py"]).
    :return: A list of matching file paths.
    """
    files_list = []  # Initialize an empty list to store matching files.

    logger.info(f"Starting recursive search in '{root_dir}' for patterns: {patterns}")

    # Loop over each pattern in the provided list.
    for pattern in patterns:
        logger.debug(f"Searching for pattern: {pattern}")
        
        # Walk through the directory tree, following symbolic links.
        for dirpath, dirnames, filenames in os.walk(root_dir, followlinks=True):
            logger.debug(f"Checking directory: {dirpath}")

            # Use glob.iglob to find files matching the current pattern in the directory.
            for filename in glob.iglob(os.path.join(dirpath, pattern)):
                logger.success(f"Found file: {filename}")
                files_list.append(filename)  # Append each matching file to the list.

    logger.info(f"Search completed. Total files found: {len(files_list)}")
    return files_list  # Return the collected list of file paths.
    
def get_files(path_src):
    """
    Get a list of all the files corresponding to the defined extensions
    :param path_src: path to directory containing the unsorted pictures
    :return: list of all corresponding files
    """
    # #
    # # def recursive_find_pic(path_src, ext):
    # #     out = []
    # #     logger.info("\t\t> ext: %s" % ext)
    # #     # for file in [f for f in os.listdir(path_src) if f.endswith('.%s' % ext.upper()) ]
    # #     files = glob.iglob("%s/**/*.%s" % (path_src, ext.upper()), recursive=True)
    # #     for file in files:
    # #         out.append(file)
    # #
    # #     # for file in [f for f in os.listdir(path_src) if f.endswith('.%s' % ext.lower()) ]
    # #     files = glob.iglob("%s/**/*.%s" % (path_src, ext.lower()), recursive=True)
    # #     for file in files:
    # #         out.append(file)
    # #     return out

    # def search_path_lib(path_src, ext):
    #     for path in Path(path_src).rglob('*.%s' % ext):
    #         logger.info(path)
    #         out.append(path)

    # pic_ext = ['png', 'jpg', 'jpeg']

    # out = []
    # logger.info("\t\t> Search images in \t %s" % path_src)
    # for ext in pic_ext:
    #     logger.info("\t\t> ext: %s" % ext)
    #     # search_path_lib(path_src, ext.upper())
    #     # for file in [f for f in os.listdir(path_src) if f.endswith('.%s' % ext.upper()) ]
    #     files = glob.iglob("%s/**/*.%s" % (path_src, ext.upper()), recursive=True)
    #     for file in files:
    #         out.append(file)

    #     # search_path_lib(path_src, ext.lower())
    # #     # for file in [f for f in os.listdir(path_src) if f.endswith('.%s' % ext.lower()) ]
    #     files = glob.iglob("%s/**/*.%s" % (path_src, ext.lower()), recursive=True)
    #     for file in files:
    #         out.append(file)

    # logger.info(" > found %d photos" % len(out))


    pic_ext = ['*.png', '*.jpg', '*.jpeg', "*.JPG", "*.PNG", "*.JPEG"]
    file_list = get_files_list_recursively_enabling_links(path_src, pic_ext)
    logger.info(" > found %d photos" % len(file_list))
    return file_list
    

#    return out


def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    if exif_data:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "DateTimeOriginal":
                value = value.replace(":", "_").replace(" ", "_")
                
                # # correct Nikkon D3500 bug
                # img = Image.open(path)
                # exif = img.getexif()
                # date_time = exif[36867]
                # device = exif[272]

                # # Nikon D3500 had the wrong time until 2020/07/03. Since we had it in 2020, all 2019 should be 2020
                # if device == 'NIKON D3500':
                #    value = value.replace("2019", "2020")

                # logger.info(f"Date and Time: {value}")
                return value


def get_date_taken(path):
    """
    Get time from meta-data
    :param path: path to file
    :return: string in format'year:month:day hours:min:sec'
    """
    
    # Example usage
    try :
        return get_exif_data(path)
    except:
        return '0000:00'

    if 0: 
        try:
            img = Image.open(path)
            exif = img.getexif()
            date_time = exif[36867]
            device = exif[272]

            # Nikon D3500 had the wrong time until 2020/07/03. Since we had it in 2020, all 2019 should be 2020
            if device == 'NIKON D3500':
                date_time = date_time.replace("2019", "2020")

            return date_time
        except:
            return '0000:00'


def collect_time(path_to_pic):
    """
    Get year and month from string in format'year:month:day hours:min:sec'
    :param path_to_pic:  path to file
    :return: strings --> year, month
    """
    full_date = get_date_taken(path_to_pic)
    logger.debug(type(full_date))
    logger.debug(full_date)
    if full_date == None:
        full_date = "0000_00_00_00_00_00"
    # logger.info("full date: ", full_date )
    full_date = full_date.replace(' ', ':').replace(':', '_')
    date = full_date.split("_")
    year, month = date[0], date[1]
    return year, month, full_date


def get_year_month_dicts(files):
    """
    Store time in a dictionary with file path as key (3 times should do the trick)
    :param files: list of files
    :return: dictionaries of years and months
    """
    years, months, full_date = {}, {}, {}
    for file in files:
        years[file], months[file], full_date[file] = collect_time(file)
    return years, months, full_date


def format_folder_name(years, months):
    """
    Identify which folders need to be created to do it only once
    """

    def format_(month):
        mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre",
                "Novembre", "Décembre"]
        return "%s - %s" % (month, mois[int(month)])

    big_lst = []
    dict = {}
    for file in years.keys():
        # tmp = "%s/%s" % (years[file], format_(months[file]))
        tmp = "%s/%s" % (years[file], months[file])
        big_lst.append(tmp)
        dict[file] = tmp

    set_ = set(big_lst)
    return set_, dict


def create_folders(path, folder_names):
    for folder in folder_names:
        name = os.path.join(path, folder)
        os.makedirs(name, mode=0o777, exist_ok=True)


def copy_pictures(copy_dict, out_path, full_date, remove_file=False):
    for file, subtree in copy_dict.items():
        # Avoid creating duplicates
        logger.info(file)
        logger.info(full_date[file])

        # file = file.split('/')[-1]
        if not full_date[file] in file:
            file = file.replace("%s_" % full_date[file], "")
            filename = "%s_%s" % (full_date[file], file.split('/')[-1])
        # keep it as it is
        else:
            filename =file.split('/')[-1]
        full_out_path = os.path.join(out_path, subtree, filename)
        if os.path.isfile(full_out_path):
            logger.info(' > No copy of "%s" to "%s" (already exists)' % (file, os.path.join(out_path, subtree, filename)))
            if remove_file:
                os.remove(file)
        else:
            if remove_file:
                logger.info(' > Move "%s" to "%s"' % (file, os.path.join(out_path, subtree, filename)))
                os.rename(file, os.path.join(out_path, subtree, filename))
            else:
                logger.info(' > Copy "%s" to "%s"' % (file, os.path.join(out_path, subtree, filename)))
                shutil.copyfile(file, os.path.join(out_path, subtree, filename))


def get_time():
    now = datetime.now()
    out = '%04d-%02d-%02d (%02d:%02d:%02d)' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    return out


def clean_empty_directories(src_dir):
    """
    Find all directories in tree. Try to delete them.
    If not empty logger.info an error message
    """
    for dirpath, _, _ in os.walk(src_dir, topdown=False):  # Listing the files
        if dirpath == src_dir:
            break
        try:
            logger.info("\t Delete directory (if empty): %s" % dirpath)
            os.rmdir(dirpath)
        except OSError as ex:
            logger.info(ex)

    for my_path in glob.glob(src_dir):
        removeEmptyFolders(my_path)


def removeEmptyFolders(path, removeRoot=True):
    'Function to remove empty folders'
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                removeEmptyFolders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and removeRoot:
        logger.info
        "Removing empty folder:", path
        os.rmdir(path)


def check_directories(in_path, out_path):
    """
    Create input/output directories if not existing
    """
    create_folders(in_path, '')
    create_folders(out_path, '')


def main(in_path, out_path):
    """
    Main routine that calls all the other ones
    :param in_path: path to input folder containing the unsorted pictures
    :param out_path: path to output folder that will contain the sorted pictures
    """
    logger.info("\t> Check directory")
    check_directories(in_path, out_path)

    logger.info("\t> Find files")
    my_files = get_files(in_path)

    logger.info("\t> Get year and months")
    years, months, full_date = get_year_month_dicts(my_files)
    logger.info(years)
    logger.info(months)
    logger.info(full_date)

    logger.info("\t> Create folder names list")
    folders, copy_dict = format_folder_name(years, months)

    logger.info("\t> Create folders")
    create_folders(out_path, folders)

    logger.info("\t> Copy and cleanup")
    copy_pictures(copy_dict, out_path, full_date, remove_file=True)

    clean_empty_directories(in_path)


if __name__ == "__main__":
    # TODO: there is a mistake in the years! 2019 instead of 2020! (Only on reflex...)

    # time loop is handled via crontab
    params = toml.load('./config.toml')
    logger.info(" > %s --> Sort" % get_time())
    main(params['Sort']['input_dir'], params['Sort']['output_dir'])
    logger.info(" > Done.")
