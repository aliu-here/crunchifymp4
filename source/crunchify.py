#!/usr/bin/python

import os
import sys
import threading
import math
import atexit
import time
import subprocess

filename = ""
try:
    filename = '"' +  sys.argv[1] + '"'
except:
    pass
audiopresent = True
videopresent = True
compressaudio = True
compressvideo = True
quality = 1 
iterations = 20
compratio = 50
fail = False
threadnum = 50
res = []

def worker(number, segment, iterations, quality):
#    print(number, segment, iterations, quality)
    filesdone = 0
    segmentlen = len(segment)
    for i in segment:
        if (videopresent and compressvideo):
            currtime = time.time()
            for j in range(iterations):
                if (i.endswith(".jpg")):
                        os.system(f"mogrify -quality {quality} -format jpg {i}")
            filesdone += 1
            currtime -= time.time()
            print(f"{filesdone}/{segmentlen} files done by thread {number}, took {-currtime} seconds")


if (not filename.endswith(".mp4\"") and filename != "-h" and filename != ""):
    newfile = "-".join(filename[1:filename.rfind('.')].split())
    os.system(f"ffmpeg -i {filename} {newfile}.mp4")
    filename = "-".join(filename[1:filename.rfind('.')].split()) + ".mp4"
    #some cursed shit above here to deal with spaces in the file name

try:
    res = subprocess.check_output(rf'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 {filename}', shell=True).strip().decode().split('x')
    framerate = float(subprocess.check_output(rf'ffmpeg -i {filename} 2>&1 | sed -n "s/.*, \(.*\) fp.*/\1/p"', shell=True))
except:
    res = [1080, 1920]
    framerate = 60

filename = filename[1:-5]
filelength = subprocess.check_output(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}.mp4').decode('utf-8')
framenum = round(int(filelength)/(1/framerate)) #get number of frames to calculate digits required for numbers 
digitsreq = math.ceil(math.log10(framenum))

outputname = filename + "compressed"

#print(filename)

#docs; it has two newlines so it's easier to read (for me, at least)
if "-h" in sys.argv or len(sys.argv) == 1:
    print("crunchify.py")
    print("crunchifies your mp4 files using ffmpeg")
    print("options:\n")
    print("-h: shows this menu\n")
    print("--noaudio: leaves out audio\n")
    print("--novideo: leaves out video\n")
    print("--nocompressaudio: doesn't compress audio\n")
    print("--nocompressvideo: doesn't compress video\n")
    print("--quality <integer>: specifies image quality of the jpg files, default is 1, limited to 100\n")
    print("--iterations <integer>: specifies number of repetitions of jpg compression, default is 20; only limit is how powerful your computer is\n")
    print("--audiocompressionratio <integer>: specifies audio compression ratio\n")
    print("--threads <integer>: specifies number of threads, between 1 and 100\n")
    print("--framerate <integer>: specifies framerate of the output video\n")
    print("--resolution <integer>x<integer>: specifies resolution; if not it's the resolution of the original video")
    print("-o <string>: specifies output file name; if not, the default is <originalname>compressed.mp4\n")
    quit()

#this is kinda stupid to have an if statement for each one but case switch is exclusive so i think this is the only way to go
if ("--noaudio" in sys.argv):
    audiopresent = False
if ("--novideo" in sys.argv):
    videopresent = False
if ("--nocompressaudio" in sys.argv):
    compressaudio = False
if ("--nocompressvideo" in sys.argv):
    compressvideo = False
if ("--quality" in sys.argv):
    try:
        quality = int(sys.argv[sys.argv.index("--quality") + 1])
    except:
        fail = True
if ("--iterations" in sys.argv):
    try:
        iterations = int(sys.argv[sys.argv.index("--iterations") + 1])
    except:
        fail = True
if ("--audiocompressionratio" in sys.argv):
    try:
        compratio = int(sys.argv[sys.argv.index("--audiocompressionratio") + 1])
    except:
        fail = True
if ("--resolution" in sys.argv):
    try:
        resolution = sys.argv[sys.argv.index("--resolution") + 1].split('x')
    except:
        fail = True
if ("-o" in sys.argv):
    try:
        outputname = sys.argv[sys.argv.index("-o") + 1]
    except:
        fail = True
if ("--threads" in sys.argv):
    try:
        threadnum = int(sys.argv[sys.argv.index("--threads") + 1])
    except:
        fail = True
if ("--framerate" in sys.argv):
    try:
        framerate = int(sys.argv[sys.argv.index("--framerate") + 1])
    except:
        fail = True

if (fail):
    print("Error: missing argument for some arguments")
    quit()

if (threadnum < 1 or threadnum > 100):
    print("bad number of threads")
    quit()

#create a directory to hold our mp3 and jpg files; since we want to clean up and running
#rm img%04d.jpg output-audio.mp3
#might be overkill and erase some files we don't want to
os.system(f"mkdir -p {filename}data")
os.system(f"cp {filename}.mp4 {filename}data")
os.chdir(f"{filename}data")
os.system(f"ffmpeg -i {filename}.mp4 -vn -c:a libmp3lame output-audio.mp3")
#4 digit file numbering; should probably raise
os.system(f"ffmpeg -i {filename}.mp4 img%0{digitsreq}d.jpg")


filesdone = 0
files = os.listdir()
jpgs = [x for x in files if x.endswith(".jpg")]
sublistlen = math.ceil(len(jpgs)/threadnum)
sublists = []
threadlist = []
if "output-audio.mp3" not in files:
    audiopresent = False

j = 0
for i in range(threadnum):
    sublist = []
    for j in range(sublistlen):
        try:
            sublist.append(jpgs[i*sublistlen+j])
        except:
            break 
    sublists.append(sublist)
    if j < sublistlen - 1:
        break

#multithreading to make it run faster
for i in enumerate(sublists):
    thread = threading.Thread(target=worker, args=(i[0], i[1], iterations, quality))
    thread.daemon = True
    threadlist.append(thread)
    thread.start()

for i in threadlist:
    i.join()

#compress w/ Lame
if (audiopresent & compressaudio):
    os.system(f"lame --comp {compratio} output-audio.mp3")

#ffmpeg create output mp4 
os.system(f'ffmpeg {"-i img%04d.jpg"*videopresent} -r {framerate} {"-i output-audio.mp3"*audiopresent} -vf "scale={res[0]}:{res[1]}" -aspect {res[0]}:{res[1]} {outputname}.mp4')

#move it back out of the working directory, then delete working directory
os.system(f"mv {outputname}.mp4 ..")

def endfunc():
#    print(res)
    os.chdir("..")
    os.system(f"rm -r {filename}data")

atexit.register(endfunc)
