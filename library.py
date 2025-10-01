# -*- coding: utf-8 -*-
#
# Filename: library.py
# Author: Jon Arce (jon.arce@gmail.com)
# Date: 2025-08-26
# Description: Class Library
#
import os
import fnmatch

class Library(object):
    condition = 'New'
    def __init__(self,configini):
        self.configini = configini

    def count(self):
        libpath = self.configini['LIBRARY']['location']
        libfiletypes = self.configini['LIBRARY']['filetypes']
        print(libpath)
        count=0
        for root, dirnames, filenames in os.walk(libpath):
            for extensions in libfiletypes.split(','):
                for filename in fnmatch.filter(filenames, extensions):
                    count += 1
        return (count)
    # What is cheaper a MacBook Air or a MacMini (M1 as It need to run the latest MAC OS?
    # Library -> Images inside, outside or mixed?
    # How to check SACD DSF files?
    # do people mix different file formats in the same directory?
    