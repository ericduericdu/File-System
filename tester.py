import fs
fs.init('abc.txt')
fs.create('a',8)
fs.create('b',4)
fd = fs.open('a','w')
fs.write(fd,'hi')
print fs.freeList
fs.write(fd,'hello')
fs.write(fd,'h')
