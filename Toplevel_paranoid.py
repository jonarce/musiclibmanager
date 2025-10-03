import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
from tkinter import filedialog
import os.path
_location = os.path.dirname(__file__)
 
import GUI_paranoid_support
 
_bgcolor'#d9d9d9'
_fgcolor ='#000000'
_tabfg1 = 'black' 
_tabfg2 = 'white' 
_bgmode = 'light' 
_tabbg1 ='#d9d9d9' 
_tabbg2 = 'gray40' 
 
_style_code_ran = 0
def _style_code():
    global _style_code_ran
    if _style_code_ran: return		
    try: GUI_paranoid_support.root.tk.call('source',
        os.path.join(_location, 'themes', 'default.tcl'))
    except: pass
    style = ttk.Style()
    style.theme_use('default')
    style.configure('.', font = "TkDefaultFont")
    if sys.platform == "win32":
        style.theme_use('winnative')	
        _style_code_ran = 1

    class Toplevel_paranoid:
        def __init__(self, top=None):
            '''This class configures and populates the toplevel window.
               top is the toplevel containing window.'''
    
            top.geometry("600x239+651+200")
            top.minsize(1, 1)
            top.maxsize(1905, 1050)
            top.resizable(1,  1)
            top.title("Verify Integrity (Paranoid Mode)")
    
            self.top = top
    
            _style_code()
            self.TProgressbar1 = ttk.Progressbar(self.top)
            self.TProgressbar1.place(relx=0.017, rely=0.879, relwidth=0.967
                    , relheight=0.0, height=19)
            self.TProgressbar1.configure(length="580")
    
            self.TButton_verify = ttk.Button(self.top)
            self.TButton_verify.place(relx=0.433, rely=0.711, height=28, width=83)
            self.TButton_verify.configure(takefocus="")
            self.TButton_verify.configure(text='''verify''')
            self.TButton_verify.configure(compound='left')
    
            self.TLabelframe_dest = ttk.Labelframe(self.top)
            self.TLabelframe_dest.place(relx=0.0, rely=0.335, relheight=0.31
                    , relwidth=1.0)
            self.TLabelframe_dest.configure(relief='')
            self.TLabelframe_dest.configure(text='''Destination Directory''')
    
            self.TButton_dest = ttk.Button(self.TLabelframe_dest)
            self.TButton_dest.place(relx=0.85, rely=0.473, height=28, width=83
                    , bordermode='ignore')
            self.TButton_dest.configure(takefocus="")
            self.TButton_dest.configure(text='''destination''')
            self.TButton_dest.configure(compound='left')
    
            self.TEntry_dest = ttk.Entry(self.TLabelframe_dest)
            self.TEntry_dest.place(relx=0.033, rely=0.541, relheight=0.284
                    , relwidth=0.807, bordermode='ignore')
            self.TEntry_dest.configure(exportselection="0")
            self.TEntry_dest.configure(takefocus="")
            self.TEntry_dest.configure(cursor="xterm")
    
            self.TLabelframe_Source = ttk.Labelframe(self.top)
            self.TLabelframe_Source.place(relx=0.0, rely=0.0, relheight=0.326
                    , relwidth=1.0)
            self.TLabelframe_Source.configure(relief='')
            self.TLabelframe_Source.configure(text='''Source Directory''')
    
            self.TEntry1 = ttk.Entry(self.TLabelframe_Source)
            self.TEntry1.place(relx=0.033, rely=0.513, relheight=0.269
                    , relwidth=0.807, bordermode='ignore')
            self.TEntry1.configure(exportselection="0")
            self.TEntry1.configure(takefocus="")
            self.TEntry1.configure(cursor="xterm")
    
            self.TButton_source = ttk.Button(self.TLabelframe_Source)
            self.TButton_source.place(relx=0.85, rely=0.513, height=28, width=83
                   , bordermode='ignore')
            self.TButton_source.configure(takefocus="")
            self.TButton_source.configure(text='''source''')
            self.TButton_source.configure(compound='left')
   
def start_up():
       GUI_paranoid_support.main()

