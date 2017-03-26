class File:
    def __init__(self, filename, size,fd):
        self.fd = fd + filename
        self.name = filename
        self.size = size  # size of file
        self.occupied = 0
        self.content = str()
        self.read = False  # if False then it's write
        self.open = False
        self.position = 0
    def writeToFile(self, writebuf):
        self.content = self.content[:self.position] + writebuf + self.content[self.position:]
        self.occupied += len(writebuf)
        self.position += len(writebuf)