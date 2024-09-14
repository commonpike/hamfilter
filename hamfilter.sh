#!/bin/sh
#
# cron script to run hamfilter

#LC_ALL=en_US.utf8
#LANG=en_US.utf8

echo ------------ >> /path/to/hamfilter.log
echo `date` >> /path/to/hamfilter.log
/path/to/hamfilter.py >> /path/to/hamfilter.log
