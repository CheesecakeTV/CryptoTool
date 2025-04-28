from Crypt_full import encrypt_full,decrypt_full
from string import ascii_letters, digits
from random import choices
from pathlib import Path

# First 3 characters are the length of the encrypted filename, zero-padded
# After that follows the filename, encrypted independently
# Then the actual file

def encrypt_file(key:str, file_path:str, output_folder:str = None, new_filename:str = None, security_multiplier:int = 1):
    """
    Encrypts a file into two files: One for the file and one for the filename.

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
    output_name_file = Path(new_filename + ".name")

    enc_file = encrypt_full(key, file_path.read_bytes(), security_multiplier=security_multiplier)
    output_folder.mkdir(parents=True,exist_ok=True)
    (output_folder / output_data_file).write_bytes(enc_file)

    enc_name = encrypt_full(key, file_path.name, security_multiplier=security_multiplier)
    (output_folder / output_name_file).write_bytes(enc_name)

def get_random_filename(length:int = 32) -> str:
    """
    Creates a random filename without ending and returns it
    :param length: Length of sequence
    :return:
    """
    return "".join(choices(ascii_letters + digits,k=length))

#temp = encrypt_full("Hallo das ist ein Test","H"*16)

#encrypt_file("Hallo/Welt\\WasGeht.txt")
encrypt_file("Passwort", "Bild.png", output_folder="test")



