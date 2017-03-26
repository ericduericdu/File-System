# fs.py file system
# Joanne Wang 9133360523
# Jeffrey Tai 998935915
# John Nguyen 998808398
# Eric Du 913327304

import io
import os
import pickle

from file import File

SystemSize = 0
freeList = []
fileList = {}
currPath = ""
systemName = ""
suspended = False


def init(fsname):
    global SystemSize
    global freeList
    global systemName
    global currPath
    global suspended
    systemName = fsname
    SystemSize = os.path.getsize(fsname)
    freeList = [None] * SystemSize
    fileList['/'] = []
    currPath = "/"


def create(filename, nbytes):
    global SystemSize
    global freeList
    global systemName
    global currPath
    if (nbytes > SystemSize):
        raise Exception('No More Space')
    filename, mkPath = getAbs(currPath, filename)
    for file in fileList[mkPath]:
        if file.name == filename:
            raise Exception('File name already exists')
    newFile = File(filename, nbytes,mkPath)
    fileList[mkPath].append(newFile)  # appended file object to file list
    save(filename, freeList, mkPath, nbytes)##########


def save(filename, freeList, mkPath, nbytes):
    global SystemSize
    data = get_native()##############
    for index in range(len(freeList)):
        if nbytes == 0:
            break
        if freeList[index] is None and (nbytes <= SystemSize):
            freeList[index] = mkPath + filename
            data[index] = "\0"
            nbytes -= 1
            SystemSize -= 1
    write_to_native(data)


def write_to_native(data):
    data = ''.join(data)
    with io.open(systemName, 'wb') as native:
        native.write(data)


def get_native():
    with io.open(systemName, 'r') as native:
        data = native.readlines()
    data = list(''.join(data).encode('UTF8'))
    return data

def open(filename, mode):  # example: filename is a
    global SystemSize
    global freeList
    global systemName
    global currPath
    global suspended
    if suspended:
        raise Exception('Cannon create. System currently suspended.')
    fileToOpen = None
    if mode not in ['r', 'w']:
        raise Exception("Invalid Mode.")
    filename, mkPath = getAbs(currPath, filename)
    dirFiles = fileList[mkPath]
    for file in dirFiles:
        if filename == file.name:
            fileToOpen = file
            break
    if fileToOpen is None:
        raise Exception("File does not exist.")
    if fileToOpen.open == True:
        raise Exception("File already open.")
    fileToOpen.open = True
    if mode == "r":
        fileToOpen.read = True
    if mode == "w":
        fileToOpen.read = False
    return mkPath + filename


def close(fd):
    global SystemSize
    global freeList
    global systemName
    global currPath
    fileToClose = isFD(fd)
    fileToClose.position = 0
    fileToClose.open = False
    fileToClose.read = False
    fileToClose.write = False


def write(fd, writebuf):
    global SystemSize
    global freeList
    global systemName
    global currPath
    F = isFD(fd)
    if (F.size - F.occupied) < len(writebuf):
        raise Exception("File not big enough")
    if F.read is True:
        raise Exception("File is read-only")
    if F.open is False:
        raise Exception("File is not open")
data = get_native()
    i = 0
    offset = len(F.content)
    for index, val in enumerate(freeList):
        if val == fd and i < len(writebuf):
            data[index + offset] = writebuf[i]
            i += 1
    write_to_native(data)
    F.writeToFile(writebuf)
################
def read(fd, nbytes):
    global SystemSize
    global freeList
    global systemName
    global currPath
    file = isFD(fd)
    retString = ""
    if file.read is not True:
        raise Exception("Error: No permission to read this file!")
    if nbytes + file.position > file.size:  # trying to read more bytes than size of file
        raise Exception("Error: trying to read more bytes than length of file.")

    for word in file.content[file.position: file.position + nbytes]:
        retString += word
        file.position += 1
    return retString


def readlines(fd):
    global SystemSize
    global freeList
    global systemName
    global currPath
    currLine = ""
    fileLines = []
    file = isFD(fd)

    if file.read is not True:
        raise Exception("Error: No permission to read this file!")
    for byte in file.content:
        currLine += byte
        if byte == "\n":
            fileLines.append(currLine)
            currLine = ""
    if currLine != "":
        fileLines.append(currLine)
    return fileLines


def length(fd):
    global SystemSize
    global freeList
    global systemName
    global currPath
    file = isFD(fd)
    return file.occupied


def pos(fd):
    global SystemSize
    global freeList
    global systemName
    global currPath
    file = isFD(fd)
    return file.position


def seek(fd, pos):
    global SystemSize
    global freeList
    global systemName
    global currPath
    file = isFD(fd)
    if pos < 0 or pos > file.size or pos > file.occupied:
        raise Exception("Incorrect position")
    file.position = pos
    return


def delfile(filename):
    global SystemSize
    global freeList
    global systemName
    global currPath
    filename, mkPath = getAbs(currPath, filename)
    data = get_native()#################
    del_fd = None
    if mkPath not in fileList:
        raise Exception("Path doesn't exist.")
    for file in fileList[mkPath]:
        if file.name == filename:
            if file.open is True:
                raise Exception("File is still open.")
            else:
                del_fd = file.fd
                SystemSize += file.size
                fileIndex = fileList[mkPath].index(file)
                del fileList[mkPath][fileIndex]
                del file
                break
    if not del_fd:
        raise Exception("File doesn't exist")
    for i in range(len(freeList)):
        if freeList[i] == del_fd:
            freeList[i] = None


def suspend():
    global SystemSize
    global freeList
    global systemName
    global currPath
    global suspended
    global fileList
    suspended = True
    for files in fileList.values():
        for file in files:
            if file.open is True:
                raise Exception("File(s) still open, cannot suspend.")
    data = get_native()
    file = io.open(systemName, 'wb')
    pickle.dump(SystemSize, file)
    pickle.dump(freeList, file)
    pickle.dump(systemName, file)
    pickle.dump(currPath, file)
    pickle.dump(fileList, file)
    pickle.dump(data, file)
    file.close
    os.rename(systemName, systemName + '.fssave')

def resume(native):
    global SystemSize
    global freeList
    global systemName
    global currPath
    global suspended
    global fileList
    suspended = False
    file = io.open(native, 'r')
    systemSize = pickle.load(file)
    freeList = pickle.load(file)
    systemName = pickle.load(file)
    currPath = pickle.load(file)
    fileList = pickle.load(file)
    data = pickle.load(file)
    os.rename(native, systemName)
    write_to_native(data)


def isdir(dirname):
    global SystemSize
    global freeList
    global systemName
    global currPath
    
    absPath = dirname.split("/")
    if (len(absPath) > 1):
        if(absPath[0] != ""):
            isPath = currPath + dirname + "/"
        else:
            isPath = dirname + "/"
    else:
        isPath = currPath + dirname + "/"

    if isPath in fileList:
        return True
    return False


def mkdir(dirname):  # Ex: b
    global SystemSize
    global freeList
    global systemName
    global currPath
    absPath = dirname.split("/")  # absPath = ['b']
    if (len(absPath) > 1):  # user gave abs path
        if(absPath[0] != ""):
            mkPath = currPath + dirname + "/"
        else:
            mkPath = dirname + "/"
    else: # user gives relative path
        mkPath = currPath + dirname + "/"  # mkPath = '/a/c/' + 'b' + '/'
    doesDirExist(mkPath, False)

    base = '/'.join(mkPath.split('/')[:-2]) + '/'
    if base not in fileList:
        raise Exception('Invalid directory name')
    fileList[mkPath] = []


def chdir(dirname):  # Ex: dirname = '/a/b'
    global SystemSize
    global freeList
    global systemName
    global currPath
    global fileList
    if dirname == '.':
        return
    if dirname == '..':  # Nope
        absPath = currPath.split("/")
        currPath = '/'.join(absPath[:-2]) + '/'
    else:
        absPath = dirname.split("/")  # absPath = ['', '']
        if (len(absPath) > 1):  # Yes
            if dirname == '/':  # Yes
                chPath = '/'  # Yes
            else:
                chPath = get_abs_path(absPath, currPath, dirname)
        else:
            chPath = currPath + dirname + "/"
        doesDirExist(chPath, True)
        currPath = chPath


def get_abs_path(absPath, currPath, dirname):
    if (absPath[0] != ""):
        chPath = currPath + dirname + "/"
    else:
        chPath = dirname + "/"
    return chPath


def deldir(dirname):  # dirname = '/a/b'
    global SystemSize
    global freeList
    global systemName
    global currPath  # currPath = '/'
    global fileList
    absPath = dirname.split("/")
    if (len(absPath) > 1):
        delPath = get_abs_path(absPath, currPath, dirname)
    else:
        delPath = currPath + dirname + "/"
    doesDirExist(delPath, True)  # doesDirExist('/a/b/', True)
    # delPath = '/a/b/'
    length = len(delPath)  # length = 5
    for key, values in fileList.items():
        if key[:length] == delPath:  # key[:5]
            for val in values:
                if val.open is True:
                    raise Exception("File(s) still open.")
                delfile(key + val.name)
            del fileList[key]
    return


def listdir(dirname):  # '/a/b'
    global SystemSize
    global freeList
    global systemName
    global currPath
    global fileList
    if dirname == '.':
        lsPath = currPath
    elif dirname == '..':
        absPath = currPath.split('/')
        lsPath = '/'.join(absPath[:-2]) + '/'
    else:
        absPath = dirname.split("/")
        if (len(absPath) > 1):
            lsPath = get_abs_path(absPath, currPath, dirname)
        else:
            lsPath = currPath + dirname + "/"
    doesDirExist(lsPath, True)
    alldir = []
    depth = len(lsPath.split('/'))
    for key in fileList.keys():
        if key[:len(lsPath)] == lsPath:
            directory = key.split('/')
            if (len(directory) - 1 == depth):
                alldir.append(directory[-2])
    return alldir


def doesDirExist(dirPath, itShouldBe):  # Ex: dirname = /a/b , itShouldBe = True
    global SystemSize
    global freeList
    global systemName
    global currPath
    global fileList
    if dirPath not in fileList and itShouldBe is True:  # if '/a/b' + 'b' + '/' , False
        raise Exception('Directory does not exist')
    if dirPath in fileList and itShouldBe is False:  # if '/a/c/' + 'b' + '/', False
        raise Exception('Directory already exists')  # raise this exception

def getAbs(currPath, filename):
    absPath = filename.split("/")
    mkPath = currPath
    if (len(absPath) > 1):
        if(absPath[0] != ""):
            mkPath = mkPath + filename.rsplit('/', 1)[0] + "/"
        else:
            mkPath = filename.rsplit('/', 1)[0] + "/"
        filename = filename.rsplit('/', 1)[1]
    return filename, mkPath

def isFD(fd):
    global SystemSize
    global freeList
    global systemName
    global currPath
    global fileList
    dirsp = fd.split('/')
    filename = dirsp[-1]
    dirPath = '/'.join(dirsp[:-1]) + '/'
    if dirPath not in fileList:
        raise Exception("No such file descriptor.")
    dirFiles = fileList[dirPath]
    for file in dirFiles:
        if filename == file.name:
            return file
    raise Exception("No such file descriptor.")



