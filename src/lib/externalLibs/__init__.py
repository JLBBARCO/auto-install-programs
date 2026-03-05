import sys, os, subprocess, threading, datetime, inspect, winreg, re, shutil, platform, time
import importlib

try:
    import customtkinter as ctk
except ImportError:
    # try installing missing requirements and re-importing
    subprocess.run(r"src\lib\install_libs.bat", shell=True)
    try:
        ctk = importlib.import_module('customtkinter')
    except Exception:
        sys.exit("customtkinter is required. Install dependencies and run again.")

# ensure the working directory is predictable when the app is frozen
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))