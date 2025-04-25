import io
from Crypt_full import encrypt_full,decrypt_full
from string import ascii_letters
from random import choices

# First 3 charakters are the length of the encrypted filename, zero-padded
# After that follows the filename, encrypted independently
# Then the actual file

def encrypt_file(file:io.BufferedReader):
    ...

temp = encrypt_full("Hallo das ist ein Test","H"*16)
print(temp)
print(len(temp))
print(ascii_letters)
print(choices(ascii_letters,k=100))

