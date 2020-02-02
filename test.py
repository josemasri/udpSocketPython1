from tkinter import *
from tkinter import filedialog

def split_file(path_file, chunk_size):
    files = []
    with open(path_file, "rb") as fi:
            buf = fi.read(chunk_size)
            while (buf):
               files.append(buf)
               buf = fi.read(chunk_size)
    return files

def create_file(fileName, dataArr):
    f = open(fileName, "w+b")
    for file in dataArr:
        f.write(file)
    f.close()

root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = ".",title = "Selecciona Archivo",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
files = split_file(root.filename, 4096)
print(f"Number of parts {len(files)}")
create_file("img2.jpg", files)
print("File {} created succesfully".format(root.filename))