
# WIP

This repo is WIP.
I will clean it up once enough functions are implemented.


# CryptoTool

Tool for encrypting and decrypting messages and files.

Its intended use is to communicate with someone about things you really want to keep private.
Don't use it for anything illegal though!

## Libraries
You need to install a couple of libraries, if you want to run the script directly:
```bash
pip install pycryptodome
pip install FreeSimpleGUI
pip install argon2pure
pip install clipboard
```

## Usage

Start/Run `main.py`.

Input goes to the upper half of the GUI, OUTPUT to the lower one.\
You can choose the types of input and output independently.

Some use-cases:
- Secret chat: Set input and output to `Text`, select `Automatic` and enter a password.
If the receiver has the same password, you can now encrypt/decrypt messages to send over
any online chat. Use the `Paste from Clipboard` button to speed things up.
Check `Automatically copy to clipboard`, then the output is copied to clipboard automatically.
- Encrypt a file to literal text so you can send it via most online chatrooms.
The receiver can decrypt the text to a file.
- Encrypt a file to a secret file with the ending `.secret`.
The filename will be preserved but encrypted.
When decrypting, the original file cann be recreated.
- View encrypted (`.secret`) files without saving them by chosing `tempfile`->`View file` as output.
The file will be deleted as soon as you close it.


## Technicalities

Everything is encrypted with AES-256.
Keys are generated using Argon2 key derivation.

To my knowledge, this is state-of-the-art and very secure, even against quantum computers.



