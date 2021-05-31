# -*- coding: utf-8 -*-

from tkinter import Tk
from TkinterGUI import SecCorrectorGUI
import os

###-----VERSION-----###
soft_version = "v4.1b"
###-----------------###
#global ventana,GUI,AAA
#
did_something = False
ventana = Tk()
ventana.soft_version = soft_version
GUI = SecCorrectorGUI(ventana)
cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))


##Create GUI Window###
def start():
    GUI.disable_buttons()
