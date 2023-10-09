import os
import subprocess

os.system("mkdir -p ~/bin")
os.system("cp crunchify.py ~/bin/crunchify")
os.system("chmod +x ~/bin/crunchify")

user = subprocess.check_output("whoami").strip().decode('utf-8')
if (user == "root"):
    print("run this as a regular user")
    quit()

bashrc = open(f"/home/{user}/.bashrc", "a")
readbashrc = open(f"/home/{user}/.bashrc", "r")
if "export PATH=$PATH:$HOME/bin" not in readbashrc.read():
    bashrc.write("export PATH=$PATH:$HOME/bin\n")
else:
    print("~/bin already added to PATH")

print("successful installation! use this to compress mp4 files terribly however much you want")
