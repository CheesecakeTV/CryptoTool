
# WIP

This is WIP.\
I will clean it up once enough functions are implemented.\
(Said every hobby-programmer ever...)

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

# Usage

Download the latest `CryptoTool.exe` from `Releases`.

If you want to run the script directly, start/run `main.py`.

## Key Exchange

How do I give the password to my partner?
If I just sand it to him, what's the point of encrypting messages?

This is where key-exchange comes in handy.
Select it in the password-tab.

You and your partner will transmit some text and form a password from them.
Even if an intruder reads these texts, he won't be able to recreate the password.

## Encrypted chatting

Enter a password, or perform a key exchange.\
Select `Text` as input and output, and `Automatic` encryption.
Check `Automatically copy to clipboard`.

### Sending
Enter your message on the upper text-input.
Click `Refresh`, or press `Control + enter`.
The message is automatically copied, so just send it to your partner.

### Receiving
Just copy the received message and click `Paste from clipboard`.

## Files

### Encrypting files

Select `File` as input and select a file.

If you just want to transmit the file, select `Tempfile` as output.
If you want to save it, select `File` instead.

Encrypted files are saved under a hidden filename with the ending `.secret`.

### Decrypting files

Select `File` as input and select your `.secret` file.

If you want to save the decrypted file, select `File` as output.

You can also just view the file by selecting `Tempfile` instead.
It will be deleted after 5 minutes or closing the program.

## Password-manager

Once you set up a connection, you can save and load the settings with the password-manager.
You find it in the `Password`-Tab.

The password-manager itself is password protected.
Choose a password you really remember, since it can't be restored.

If you choose a title and subtitle that match another entry, it will be overwritten.


# Technicalities

Everything is encrypted with AES-256.
Keys are generated using Argon2 key derivation.

To my knowledge, this is state-of-the-art and very secure, even against quantum computers.

Key exchange is performed using Diffie-Hellmann algorithm with ECC (Eliptic-Curve-Cryptography).

