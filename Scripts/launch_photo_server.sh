#!/bin/bash

alias python3="/Users/qdouasbin/Python/py3p13/bin/python3"

clear
#cd /External/PhotosBambinage
#cd Scripts
echo " > Organize photos"
python3 organize_pics.py >> log_organize_pics.txt &
#/usr/bin/python3.7 organize_pics.py >> log_organize_pics.txt &
echo " > Organize videos"
python3 organize_videos.py >> log_organize_videos.txt &
#/usr/bin/python3.7 organize_videos.py >> log_organize_videos.txt &
echo " > Create small photos"
#/usr/bin/python3.7 create_small.py  >> log_create_small.txt & 
python3 create_small.py  >> log_create_small.txt & 
echo " > Done"
cd $HOME
