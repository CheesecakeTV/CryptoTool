import os
from Crypto.Cipher import AES
import argon2pure


def encrypt(data:bytes,key:bytes) -> tuple[bytes,bytes,bytes]:
    """
    Standard encryption with AES (GCM)
    :param data:
    :param key: Should be 32 byte long
    :return: encrypted data, nonce, tag
    """
    crypter = AES.new(key,AES.MODE_GCM,mac_len=16)
    nonce = crypter.nonce

    enc_data,tag = crypter.encrypt_and_digest(data) # tag ist immer 16 byte lang

    return enc_data,nonce,tag

def decrypt(enc_data:bytes,key:bytes,nonce:bytes,tag:bytes=None) -> bytes:
    """
    Standard decryption of AES (GCM)
    :param enc_data:
    :param key:
    :param nonce: Optained from encrypt()
    :param tag: Optional. Prevents data manipulation. Optained from encrypt()
    :return: Decrypted bytes
    """
    crypter = AES.new(key,AES.MODE_GCM,nonce=nonce)

    data = crypter.decrypt(enc_data)

    if tag is not None:
        crypter.verify(tag)

    return data

def derive_key(key:str|bytes,salt:bytes=None,length_bytes:int=32,salt_len:int=16) -> tuple[bytes,bytes]:
    """
    Derives a key from passed string with the length of length_bytes.
    If no salt is passed, a random one with length 16 will be generated.
    :param salt_len: If no salt is passed, a salt with this length is used
    :param salt: Pass to generate the same key every time
    :param key: Key from e.g. a user
    :param length_bytes: Length of the derived key
    :return: Key (hashed), salt
    """
    if isinstance(key,str):
        key = key.encode()

    if salt is None:
        salt = os.urandom(salt_len)

    key_hash = argon2pure.argon2(key, salt, 10, 32, parallelism=1, tag_length=length_bytes)

    return key_hash,salt

if __name__ == "__main__":
    # Test-Code for this script

    the_key,_ = derive_key("Hallo Welt")

    print(the_key)
    print(len(the_key))

    temp_data,temp_nonce,temp_tag = encrypt(b"Hallo Weltttttttttttttttttttttttttttttt Hallo Weltttttttttttttttttttttttttttttt Hallo Weltttttttttttttttttttttttttttttt",the_key)
    print("Data:",temp_data)
    print("Nonce:",temp_nonce,len(temp_nonce))
    print("Tag:",temp_tag,len(temp_tag))

    print(decrypt(temp_data,the_key,temp_nonce))

