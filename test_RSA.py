from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

#mykey = RSA.generate(3072)
mykey = RSA.generate(1024)

print(mykey.has_private())
private = mykey.export_key(format="DER")
public = mykey.public_key().export_key(format="DER")

print(len(private),private)
print(len(public),public)

encrypter = PKCS1_OAEP.new(RSA.import_key(public))
decrypter = PKCS1_OAEP.new(mykey)

print(encrypter,decrypter)

data = b"Hallo Welt"
enc_data = encrypter.encrypt(data)

print()
print(enc_data)

dec_data = decrypter.decrypt(enc_data)
print(dec_data)

