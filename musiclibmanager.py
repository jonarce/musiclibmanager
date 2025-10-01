#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Filename: musiclibmanager.py
# Author: Jon Arce (jon.arce@gmail.com)
# Date: 2025-08-21
# Description: GUI to manage all musiclibrary functionality.
#

# Import the required libraries
# ttk - tkinter modern widgets
from tkinter import *
from tkinter import ttk, messagebox
# ini file reader
import configparser
import subprocess
# create log files
import logging
# support for SQLite3 database
import sqlite3
import fnmatch, os


# fileNewItem
def addNewMusic(event):
    print('newAddMusic')
    # Perform new add music tasks here

# fileQuit
def fileQuit(event):
    logger.info('Music Library Manager ended.')
    rootframe.Close()

# integrityVerify
def integrityVerify(event):
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
def integrityParanoid(event):
    # read configuration ini file
    config = configparser.ConfigParser()
    config.read('musiclibmanager.ini')

    # set logging
    logger = logging.getLogger(__name__)
    #logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    logging.basicConfig(filename=config['APP']['logfile'], 
                        format='%(asctime)s - %(levelname)s - %(message)s', 
                        level=logging.DEBUG)
    logger.info('Integrity paranoid started.')

    libpath = config['LIBRARY']['location']
    logger.debug(f"Library path: {libpath}")
    # include cover images in the checksum calculation
    if config['COVER']['imagenames']:
        scanfiletypes = config['LIBRARY']['filetypes'] + ','+ config['COVER']['imagenames']
    else:
        scanfiletypes = config['LIBRARY']['filetypes']
    logger.debug(f"Library file types: {scanfiletypes}")
    checksumtool = config['LIBRARY']['checksumtool'] 
    logger.debug(f"Library checksum tool: {checksumtool}")
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
                result = subprocess.run([checksumtool, ' ', os.path.join(root, filename)],
                capture_output=True,text=True)  # Python >= 3.7 only
                # just get the checksum output (till the first whitespace)
                chksum=result.stdout
                error=result.stderr

                if error is None or not str(error).strip():
                    logger.error(f"Checksum error: {error}")
                else:
                    chksum=chksum.split(None,1)[0] # only the checksum (as it comes with the name of the file added at the end)
                    logger.debug(f"Checksum: {chksum}")
                    cursor.execute("INSERT INTO checksum (file, chksumtype, chksum) VALUES (?, ?, ?)",
                                   (os.path.join(root, filename), checksumtype, chksum))
                    cursor.connection.commit()

    sqliteConnection.close()
    logger.debug("Integrity check completed.")


# main #

# read configuration ini file
config = configparser.ConfigParser()
config.read('musiclibmanager.ini')

# Initialize the application 
root = Tk()
root.title('Music Library Manager')
root.geometry("3051x2034")

# add the menunar
root.option_add('*tearOff', FALSE)
m = Menu(root)
m_edit = Menu(m)


# background image
bg = PhotoImage(file = "music.jpg")

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

#
m.add_cascade(menu=m_edit, label="Edit")
m_edit.add_command(label="Paste", command=lambda: root.focus_get().event_generate("<<Paste>>"))
m_edit.add_command(label="Find...", command=lambda: root.event_generate("<<OpenFindDialog>>"))
root['menu'] = m

# create the File and Edit menus
#menu_file = Menu(menubar)
#menu_edit = Menu(menubar)
#menubar.add_cascade(menu=menu_file, label='File')
#menubar.add_cascade(menu=menu_edit, label='Edit')

#menubar = Menu(root)
#root.config(menu=menubar)

# create a menu
#fileMenu = Menu(menubar)

# add a menu item to the menu
#fileMenu.add_command(
#    label='Exit',
#    command=root.destroy
#)

# integrity
#integrityMenu = Menu(menubar)
#integrityItem = integrityMenu.add_command(label='&Verify Integrity', command=integrityVerify)
#integrityItem = integrityMenu.add_command(label='&Verify Paranoid Mode', command=integrityParanoid)

# Start the event loop 
root.mainloop()

# End of musiclibmanager.py