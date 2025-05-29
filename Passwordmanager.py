from Globals import appdata
from dataclasses import dataclass
import FreeSimpleGUI as sg
import pickle
from datetime import datetime as dt
from Crypto_full import encrypt_full,decrypt_full

manager_data = appdata / "Passwordmanager.pm"
password:str|None = None
security_multiplier = 3

@dataclass
class Entry:
    Title:str       # More of a group name
    Subtitle:str    # Specified usage
    Created:dt  # Time created
    data:dict

    def __hash__(self):
        return hash((self.Title,self.Subtitle))

    def __eq__(self, other):
        return hash(self) == hash(other)

def get_password() -> str|None:
    """
    Returns or asks for the manager-password
    :return:
    """
    global password

    if not manager_data.exists():
        sg.theme("DarkGray11")
        answer = sg.popup_get_text("First time using password-manager.\n"
                                   "Please set a password.\n"
                                   "\nAttention!\nIf you forget the password,\nyou can't access the passwordmanager\nwithout deleting all saved entries."
                                   , title="Setup Password", font="Any 12",keep_on_top=True,password_char="*")

        if not answer:
            return None

        password = answer

        manager_data.write_bytes(
            encrypt_full(
                password,
                pickle.dumps(set()),
                security_multiplier=security_multiplier
            )
        )

    elif password is None:
        answer = sg.popup_get_text("Enter password for passwordmanager",title="Password",font="Any 12",password_char="*")
        if answer is None:
            return None

        password = answer

    try:
        decrypt_full(
            password,
            manager_data.read_bytes(),
            security_multiplier=security_multiplier,
        )
    except ValueError:
        sg.popup_error("Wrong password, or file was modified!")
        password = None
        return get_password()

    return password

def _load_entries() -> set[Entry]:
    """
    Returns saved passwords
    :return:
    """
    ...

print(manager_data)
print(get_password())
