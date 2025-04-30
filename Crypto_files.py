from Crypt_full import encrypt_full,decrypt_full
from string import ascii_letters, digits
from random import choices
from pathlib import Path
import os
import tempfile
import threading


def encrypt_file(key:str, filename:str, data:bytes, security_multiplier:int = 1) -> bytes:
    """
    Encrypts a file and the filename into a single file:

    Decrypted file looks like this (without separation chars):
    - First character: Length of the filename (one byte)
    - Filename
    - File-Data

    :param data: file-data
    :param filename: file-name (is encrypted with the data)
    :param security_multiplier: Security multiplier for key derivation
    :param key: Clear password for the file
    :return:
    """
    enc_data = chr(len(filename)).encode() + filename.encode() + data

    return encrypt_full(key, enc_data, security_multiplier=security_multiplier)

def encrypt_file_full(key:str, file_path:str, output_folder:str = None, new_filename:str = None, security_multiplier:int = 1) -> str:
    """
    Encrypts a file and saves the encrypted file somewhere

    :param security_multiplier: Security multiplier for key derivation
    :param key: Clear password for the file
    :param new_filename: If given, this filename will be used instead of a random one
    :param file_path: Path to file to be encrypted
    :param output_folder: If given, encrypted file will be saved in this directory
    :return:
    """
    file_path = Path(file_path)
    old_folder = Path(*file_path.parts[:-1])

    if output_folder is None:
        output_folder = old_folder

    if new_filename is None:
        new_filename = get_random_filename()

    output_folder = Path(output_folder)
    output_data_file = Path(new_filename + ".secret")

    filename = file_path.name
    assert len(filename) < 256
    file_data = file_path.read_bytes()

    enc_file = encrypt_file(key,filename,file_data,security_multiplier=security_multiplier)

    output_folder.mkdir(parents=True,exist_ok=True)
    output_data_file = output_folder / output_data_file
    output_data_file.write_bytes(enc_file)

    return output_data_file.as_posix()

def decrypt_file(key:str, data:bytes, security_multiplier:int = 1) -> tuple[bytes,str]:
    """

    :param data: Encrypted file content
    :param security_multiplier: Has to match security_multiplier from encryption
    :param key: Readable key
    :return: Decrypted data, decrypted name
    """
    dec_file = decrypt_full(key,data,security_multiplier=security_multiplier)

    len_name = ord(dec_file[0:1])
    file_name = dec_file[1:len_name + 1].decode()
    file_data = dec_file[len_name + 1:]

    return file_data, file_name

def decrypt_file_full(key:str, file_path:str, output_folder:str = None, security_multiplier:int = 1) -> str:
    """

    :param security_multiplier: Has to match security_multiplier from encryption
    :param output_folder: Where to put the file. Pass None to use the same as input file-path
    :param key: Readable key
    :param file_path:
    :return:
    """
    file_path = Path(file_path)
    old_folder = Path(*file_path.parts[:-1])

    if output_folder is None:
        output_folder = old_folder

    output_folder = Path(output_folder)

    file_data, file_name = decrypt_file(key,file_path.read_bytes(),security_multiplier=security_multiplier)

    file_name = output_folder / Path(file_name)
    output_folder.mkdir(parents=True, exist_ok=True)
    file_name.write_bytes(file_data)

    return file_name.as_posix()

def get_random_filename(length:int = 32) -> str:
    """
    Creates a random filename without ending and returns it
    :param length: Length of sequence
    :return:
    """
    return "".join(choices(ascii_letters + digits,k=length))

def _temporarely_view_file(filename:str,data:bytes) -> None:
    """
    Should be started on a thread!
    Saves and opens a file from a temporary directory that gets deleted after closing
    :param filename: Name of temporary file. Important for the ending
    :param data:
    :return:
    """
    direct = tempfile.TemporaryDirectory()
    temp_path = Path(direct.name,filename)
    temp_path.write_bytes(data)

    os.system(temp_path.as_posix())

    direct.cleanup()

def temporarely_view_encrypted_file(key:str, data:bytes, security_multiplier:int = 1):
    """
    Saves and opens an encrypted file from a temporary directory that gets deleted after closing

    :param key:
    :param data:
    :param security_multiplier:
    :return:
    """
    data, filename = decrypt_file(key, data, security_multiplier=security_multiplier)
    threading.Thread(target=_temporarely_view_file,args=(filename,data)).start()

#temp = encrypt_full("Hallo das ist ein Test","H"*16)

#encrypt_file("Hallo/Welt\\WasGeht.txt")
# temp = encrypt_file_full("Passwort", "Bild.png", output_folder="test")
# decrypt_file_full("Passwort",temp)

# temporarely_view_encrypted_file("Passwort", Path("test/bMXTPArl4qwIsoMOjEZ7r4b9PcI12jrv.secret").read_bytes())



