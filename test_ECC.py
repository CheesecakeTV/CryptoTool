from Crypto.PublicKey import ECC

mykey = ECC.generate(curve="Ed25519")

public = mykey.public_key().export_key(format="DER")
print(public)
private = mykey.export_key(format="DER")
print(private)

print(mykey.has_private())
