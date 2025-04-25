import tempfile
import os
import time

direct = tempfile.TemporaryDirectory()
print(direct.name)

file = tempfile.TemporaryFile(dir=direct.name,suffix=".txt",delete=False)
print(file.name)

input()
file.close()
os.system(file.name)
input()
direct.cleanup()







