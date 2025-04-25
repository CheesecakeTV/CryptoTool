from Crypt_full import encrypt_full,decrypt_full


with open("Bild.png","rb") as f:
    enc = encrypt_full("Hallo Welt",f.read())

with open("Bild_enc.png","wb") as f:
    f.write(enc)

with open("Bild_dec.png","wb") as f:
    f.write(decrypt_full("Hallo Welt",enc))




