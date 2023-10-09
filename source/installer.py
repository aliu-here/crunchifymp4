import os
import subprocess

user = subprocess.check_output("whoami").strip().decode('utf-8')

crunchifyexists = True 
changes = True
try:
    oldcrunchify = open(f"/home/{user}/bin/crunchify", "r")
    newcrunchify = open("crunchify.py", "r")
    changes = oldcrunchify.read() == newcrunchify.read()
except:
    crunchifyexists = False

os.system("mkdir -p ~/bin")
os.system("cp crunchify.py ~/bin/crunchify")
os.system("chmod +x ~/bin/crunchify")

if (user == "root"):
    print("run this as a regular user")
    quit()

bashrc = open(f"/home/{user}/.bashrc", "a")
readbashrc = open(f"/home/{user}/.bashrc", "r")
if "export PATH=$PATH:$HOME/bin" not in readbashrc.read():
    bashrc.write("export PATH=$PATH:$HOME/bin\n")
else:
    print("~/bin already added to PATH")

if (not crunchifyexists):
    print("successful installation! use this to compress mp4 files terribly however much you want")
elif (changes):
    print("successful update!")
