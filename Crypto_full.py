from Crypto_primitives import derive_key,decrypt,encrypt


def encrypt_full(key:str,data:str|bytes,security_multiplier:int=1) -> bytes:
    """
    Encrypt some data
    :param security_multiplier:
    :param key: Clear key, non-derived
    :param data:
    :return:
    """
    if isinstance(data,str):
        data = data.encode()

    key_derived,salt = derive_key(key,length_bytes=32,salt_len=16,security_multiplier=security_multiplier)
    enc_data,nonce,tag = encrypt(data,key_derived)

    return tag + nonce + salt + enc_data

def decrypt_full(key:str,data:bytes,as_str:bool = False,security_multiplier:int=1,verify:bool=True) -> bytes|str:
    """
    Decrypt data from encrypt_full
    :param verify: If the message was modified, this will raise a ValueError
    :param security_multiplier:
    :param as_str: Decode Data
    :param key: Clear key, non-derived
    :param data: Byte-array optained from encrypt_full()
    :return:
    """
    tag, nonce, salt, enc_data = data[0:16], data[16:32], data[32:48], data[48:]

    if not verify:
        tag = None

    key_derived,_ = derive_key(key,salt=salt,length_bytes=32,security_multiplier=security_multiplier)
    decrypted = decrypt(enc_data,key_derived,nonce,tag)

    if as_str:
        return decrypted.decode()

    return decrypted






