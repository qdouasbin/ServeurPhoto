#!/bin/bash

cd /External/PhotosBambinage
cd Scripts
echo " > Organize photos"
/usr/bin/python3.7 organize_pics.py >> log_organize_pics.txt &
echo " > Organize videos"
/usr/bin/python3.7 organize_videos.py >> log_organize_videos.txt &
echo " > Create small photos"
/usr/bin/python3.7 create_small.py  >> log_create_small.txt & 
echo " > Done"
cd $HOME
