# Serveur Photo

Organize and resize your photos. 
The input photos are to be pasted in a dropbox folder, e.g.  `Dropbox`.
The date and time data is extracted from metadata and is used to organize the files in a `YYYY/MM` directory tree. 
Photos are automatically renamed to be easily browsed in chronological order.

If the picture is larger than a user-defined threshold, say 1MB, a miniature version of the image is also created and sorted under the `YYYY/MM` format.

An example folder tree would be:

The configuration file `config.toml` is used to specify the input/output directories and the other user-defined parameters.

## Install

### Get the sources

If `git` is installed on your system, your can clone the repository by running.

```bash
cd ~
mkdir serveur_photo
cd serveur_photo
git clone https://github.com/qdouasbin/ServeurPhoto.git 
```

Otherwise, simply download the ZIP file from [https://github.com/qdouasbin/ServeurPhoto](https://github.com/qdouasbin/ServeurPhoto) and extract it in the directory of your choice.

### Install the required Python packages

Use the `requirement.txt` file to ensure that the Python libraries are installed.

```bash
cd ~/serveur_photo/Scripts/
pip3 install requirement.txt
```

## Run the scripts

For instance, creating small pictures can be done by:

 1. Copy/pasting your pictures, or folder containing pictures, in the `Dropbox` directory
 2. Running the `organize_pics.py` script
 3. Running the `create_small.py` script
 
Step 2 is done by going to the folder containing the scripts and running the script via the python interpreter:

```bash
cd ~/serveur_photo/Scripts/
python3 organize_pics.py
```

Step 3:

```bash
cd ~/serveur_photo/Scripts/
python3 create_small.py
```

## Example of config file

```TOML
#
# Configuration file of the picture save/organization/treatment
#
[Sort]
# Input directory (Dropbox), dir. where the new, non-organized, non-treated pictures are to be sought
input_dir = "../Dropbox"
# Output directory for photos organized by YYYY/MM/
output_dir = "../Sorted/Large"

[Resize]
# Size (in MegaBytes) of the "small" pictures
size_small = 1.0
# Output directory
small_dir = "../Sorted/Small"

[Videos]
video_dir = "../Sorted/Videos"
```
