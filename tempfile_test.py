import tempfile
import os
import time

direct = tempfile.TemporaryDirectory()
print(direct.name)

#file = tempfile.TemporaryFile(dir=direct.name,suffix=".txt",delete=False)
#print(file.name)

with open("Bild.png","rb") as f:
    raw = f.read()

name = direct.name + "/" + "Bild.png"

with open(name,"wb") as f:
    f.write(raw)

#os.system(name)
os.system("start " + direct.name)
input()

#file.close()
#os.system(file.name)
direct.cleanup()
#del direct






