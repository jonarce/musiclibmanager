`   ``          qw#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Filename: musiclibmanager.py
# Author: Jon Arce (jon.arce@gmail.com)
# Date: 2025-08-21
# Description: GUI to manage all musiclibrary functionality.
#

# Import the required libraries
# ttk - tkinter modern widgets (will replace classic ones)
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
# ini file reader
import configparser
import subprocess
# create log files
import logging
# support for SQLite3 database
import sqlite3
import fnmatch, os, hashlib
# Classes for eacj menu item
from Toplevel_paranoid import Toplevel_paranoid

def get_sha256_hash(file_path):
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

# fileNewItem
def addNewMusic():
    print('newAddMusic')
    # Perform new add music tasks here

# fileQuit
def fileQuit():
    logger.info('Music Library Manager ended.')
    root.Close()

# integrityVerify
def integrityVerify():
    logger.info('Integrity verifier started.')
    # Perform integrity verification tasks here
    logger.info('Integrity verifier ended.')

def string_to_hex(input_string):
    # First, encode the string to bytes
    bytes_data = input_string.encode('utf-8')

    # Then, convert bytes to hex
    hex_data = bytes_data.hex()

    return hex_data

# integrityParanoid will calculate the checksum of each music file 
# and compare it to the stored checksum (inside an sqlite database)
def menu_integrityChecksum():
    # read configuration ini file
    config = configparser.ConfigParser()
    config.read('musiclibmanager.ini')

    # set logging
    logger = logging.getLogger(__name__)
    #logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    logging.basicConfig(filename=config['APP']['logfile'], 
                        format='%(asctime)s - %(levelname)s - %(message)s', 
                        level=logging.DEBUG)
    logger.info('Integrity Calc-Checksum started.')

    child_window = Toplevel()
    canvas = Canvas(child_window, height=500, width=600)
    canvas.pack()

    libpath = config['LIBRARY']['location']
    #libpath = filedialog.askopenfilename(title="Select Library Directory", filetype=(('text files''*.txt'),('all files','*.*')))
    libpath = filedialog.askdirectory()
    ttk.Label(child_window, text=libpath, font=13).pack()
    logger.debug(f"Library path: {libpath}")
    # include cover images in the checksum calculation
    if config['COVER']['imagenames']:
        scanfiletypes = config['LIBRARY']['filetypes'] + ','+ config['COVER']['imagenames']
    else:
        scanfiletypes = config['LIBRARY']['filetypes']
    logger.debug(f"Library file types: {scanfiletypes}")
    checksumtype = config['LIBRARY']['checksumtype']
    logger.debug(f"Library checksum type: {checksumtype}")

    sqliteConnection = sqlite3.connect('./data/paranoid.db')
    cursor = sqliteConnection.cursor()

    # create checksum table if not exists
    cursor.execute(config['LIBRARY']['checksumtable'])
    cursor.connection.commit()
    
    #  erase all previous records (SQLite does not have TRUNCATE TABLE command)
    cursor.execute("DELETE FROM checksum;")
    cursor.connection.commit()

    # check all files in the library
    for root, dirnames, filenames in os.walk(libpath):
        for extensions in scanfiletypes.split(','):
            for filename in fnmatch.filter(filenames, extensions):
                logger.debug(os.path.join(root, filename))
                # calculate checksum
                chksum=get_sha256_hash(os.path.join(root, filename))
                error=FALSE

                if error is None or not str(error).strip():
                    logger.error(f"Checksum error: {error}")
                else:
                    logger.debug(f"Checksum: {chksum}")
                    cursor.execute("INSERT INTO checksum (libpath,file,chksumtype,chksum) VALUES (?, ?, ?, ?)",
                                   (libpath, os.path.join(root, filename), checksumtype,chksum))
                    cursor.connection.commit()

    sqliteConnection.close()
    logger.debug("Integrity check completed.")

def menu_integrityParanoid():
    global paranoid_window
    paranoid_window = IntegrityParanoid()

# main #

# read configuration ini file
config = configparser.ConfigParser()
config.read('musiclibmanager.ini')

# Initialize the application 
root = Tk()
#root.geometry("1525x1017")
root.geometry("762x508")
root.title('Music Library Manager')

# add the menubar
root.option_add('*tearOff', FALSE)
menu_bar = Menu(root)


# background image
bg = PhotoImage(file = "bg_music.png")

# Show image using label
labelbg = Label( root, image = bg)
labelbg.place(x = 0, y = 0)

# set logging
logger = logging.getLogger(__name__)
#logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(filename=config['APP']['logfile'], 
                        format='%(asctime)s - %(levelname)s - %(message)s', 
                        level=logging.DEBUG)
logger.info('Music Library Manager started')

# create the File and Edit menus
menubar = Menu(root)
root.config(menu=menubar)
menu_file = Menu(menubar)
menu_integrity = Menu(menubar)
menu_cover = Menu(menubar)
menubar.add_cascade(menu=menu_file, label='File')
menubar.add_cascade(menu=menu_integrity, label='Integrity')
menubar.add_cascade(menu=menu_cover, label='Cover')

# add a menu item to the menu
menu_file.add_command(
    label='Exit',
    command=root.destroy)

# integrity
menu_integrity.add_command(
    label='Calc CheckSums',
    command=menu_integrityChecksum)

#integrityItem = integrityMenu.add_command(label='&Verify Integrity', command=integrityVerify)
integrityItem = menu_integrity.add_command(
    label='Integrity Paranoid Mode', 
    command=menu_integrityParanoid)

# Start the event loop 
root.mainloop()

# End of musiclibmanager.py