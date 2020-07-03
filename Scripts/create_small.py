"""
This script:
    1) searches for "real size" pictures
    2) if size of picture is too large resize it (properly!)
    3) copy it to the good place
"""
import os
import glob
import shutil
import time
import organize_pics as ogpic
import numpy as np

from datetime import datetime

import toml

from PIL import Image


def create_small_size_img(filename, size_MB, size_max_MB):
    print("Creating small image")
    image = Image.open(filename)
    size_w, size_h = image.size
    factor = np.sqrt(size_MB / size_max_MB)
    new_size = int(size_w / factor), int(size_h / factor)
    try:
        image = image.resize(new_size, Image.ANTIALIAS)
    except OSError:
        print("Cannot process image %s. File is probably damaged!" % filename)
    return image


def copy_small_pictures(copy_dict, out_path, size_max_MB):
    for file, subtree in copy_dict.items():
        filename = file.split('/')[-1]
        ext = filename.split('.')[-1]
        small_file_name = filename.replace(".%s" % ext, "_small.%s" % ext)
        full_out_path = os.path.join(out_path, subtree, filename)
        full_out_path_small = os.path.join(out_path, subtree, small_file_name)
        size_file = 1e-6 * os.stat(file).st_size

        # move file to "small" if it is already smaller than the limit
        if size_file <= size_max_MB:
            if not os.path.exists(full_out_path):
                print("\tMove small picture: %s\t-->\t%s" % (file, full_out_path))
                os.rename(file, os.path.join(out_path, subtree, filename))

        # resize...Do it like a pro!
        else:
            if not os.path.exists(full_out_path_small):
                print("\t> resize %s" % file)
                small_img = create_small_size_img(file, size_file, size_max_MB)
                small_img.save(full_out_path_small)


def main(in_path, out_path, size_max_MB):
    print("\t> Find files")
    my_files = ogpic.get_files(in_path)

    print("\t> Get year and months")
    years, months = ogpic.get_year_month_dicts(my_files)

    print("\t> Create folder names list")
    folders, copy_dict = ogpic.format_folder_name(years, months)

    print("\t> Create folders")
    ogpic.create_folders(out_path, folders)

    print("\t> Create Small pictures and copy them")
    copy_small_pictures(copy_dict, out_path, size_max_MB)


if __name__ == "__main__":
    # time loop is handled via crontab
    params = toml.load('./config.toml')
    input_path = params['Sort']['output_dir']
    output_path = params['Resize']['small_dir']
    size_small_mb = float(params['Resize']['size_small'])

    print(" > %s --> Resize" % ogpic.get_time())
    main(input_path, output_path, size_small_mb)
    print(" > Done.")
