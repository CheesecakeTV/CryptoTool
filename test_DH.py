from Crypto.PublicKey import ECC
from Crypto.Hash import SHAKE128
from Crypto.Protocol.DH import key_agreement

# Key derivation function
def kdf(x):
    return SHAKE128.new(x).read(32)

# In a real scenario, this key already exists
U = ECC.generate(curve='Ed25519')
U_pub = U.public_key()

# In a real scenario, this key is received from the peer
# and it is verified as authentic
V = ECC.generate(curve='Ed25519')
V_pub = V.public_key()
V_pub = V_pub.export_key(format="DER")

V_pub = ECC.import_key(V_pub)

session_key = key_agreement(static_priv=U, static_pub=V_pub, kdf=kdf)
sesson_key_same = key_agreement(static_priv=V, static_pub=U_pub, kdf=kdf)

# session_key is an AES-256 key, which will be used to encrypt
# subsequent communications

print(session_key)
print(sesson_key_same)
