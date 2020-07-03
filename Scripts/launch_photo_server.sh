#!/bin/bash

cd /External/PhotosBambinage
cd Scripts
/usr/bin/python3.7 organize_pics.py >> log_organize_pics.txt &
/usr/bin/python3.7 create_small.py  >> log_create_small.txt & 
cd $HOME
