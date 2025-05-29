from collections.abc import Iterable
from Globals import appdata
from dataclasses import dataclass,field
import FreeSimpleGUI as sg
import pickle
from datetime import datetime as dt
from Crypto_full import encrypt_full,decrypt_full

manager_data = appdata / "Passwordmanager.pm"
_password: str | None = None
security_multiplier = 3

@dataclass
class Entry:
    Title:str       # More of a group name
    Subtitle:str=""    # Specified usage
    Created:dt=field(default_factory=dt.now)  # Time created
    data:dict=field(default_factory=dict)

    def __hash__(self):
        return hash((self.Title.casefold(),self.Subtitle.casefold()))

    def __eq__(self, other):
        return hash(self) == hash(other)

def _get_password() -> str|None:
    """
    Returns or asks for the manager-password
    :return:
    """
    global _password

    if not manager_data.exists():
        sg.theme("DarkGray11")
        answer = sg.popup_get_text("First time using password-manager.\n"
                                   "Please set a password.\n"
                                   "\nAttention!\nIf you forget the _password,\nyou can't access the passwordmanager\nwithout deleting all saved entries."
                                   , title="Setup Password", font="Any 12",keep_on_top=True,password_char="*")

        if not answer:
            return None

        _password = answer

        manager_data.write_bytes(
            encrypt_full(
                _password,
                pickle.dumps(set()),
                security_multiplier=security_multiplier
            )
        )

    elif _password is None:
        sg.theme("DarkGray11")
        answer = sg.popup_get_text("Enter password for passwordmanager",title="Password",font="Any 12",password_char="*")
        if answer is None:
            return None

        _password = answer

    try:
        decrypt_full(
            _password,
            manager_data.read_bytes(),
            security_multiplier=security_multiplier,
        )
    except ValueError:
        sg.theme("DarkGray11")
        sg.popup_error("Wrong password, or file was modified!",font="Any 12")
        _password = None
        return _get_password()

    return _password

def _load_entries() -> set[Entry]:
    """
    Returns saved passwords
    :return:
    """
    if _get_password() is None:
        return set()

    return pickle.loads(
        decrypt_full(
            _password,
            manager_data.read_bytes(),
            security_multiplier=security_multiplier
        )
    )

def _save_entries(entries:set[Entry]):
    """
    Saves the entries encrypted to the file
    :param entries:
    :return:
    """
    if _get_password() is None:
        return None

    manager_data.write_bytes(
        encrypt_full(
            _password,
            pickle.dumps(entries),
            security_multiplier=security_multiplier,
        )
    )

def _get_layout() -> list[list[sg.Element]]:
    """Window-layout"""

    layout = [
        # [
        #     sg.T("Search:"),
        #     sg.In(expand_x=True,key="Searchbar",enable_events=True)
        # ],
        [
            sg.Table(
                [],
                headings=["Title","Subtitle","Created/Modified"],
                col_widths=[20,50,15],
                auto_size_columns=False,
                size=(0,15),
                key="Table",
                justification="left",
            )
        ],[
            sg.Button("Apply",key="Apply"),
            sg.Button("Delete Entry",key="Delete"),
        ]
    ]

    return layout

def _entries_to_table(entries:Iterable[Entry]) -> list[list[str]]:
    """
    Return for layout-Table
    :param entries:
    :return:
    """
    return [
        [
            e.Title,
            e.Subtitle,
            e.Created.strftime("%d.%m.%Y %H:%M"),
        ] for e in entries
    ]

def new_entry(title:str,subtitle:str,data:dict) -> bool:
    """
    Create a new password-entry
    :param title:
    :param subtitle:
    :param data:
    :return:
    """
    title = title.strip()
    subtitle = subtitle.strip()

    if _get_password() is None:
        return False

    entries:set[Entry] = _load_entries()
    entries.add(Entry(title,subtitle,data=data))
    _save_entries(entries)

    return True

def passwordmanager() -> dict|None:
    """
    Full passwordmanager.
    Returns password-data if it is supposed to be opened
    :return:
    """
    sg.theme("DarkGray11")

    entries:list[Entry] = list(_load_entries())
    if not entries:
        return None

    layout = _get_layout()

    w = sg.Window("Password-Manager",layout,finalize=True)
    w.read(timeout=10)
    w["Table"].bind("<Double-Button-1>","_Double")

    w["Table"](_entries_to_table(entries))

    while True:
        e,v = w.read()
        print(e)

        if e is None:
            return None

        if e in ["Table_Double","Apply"] and v["Table"]:
            w.close()
            return entries[v["Table"][0]].data

        if e == "Delete" and v["Table"] and "Yes" == sg.popup_yes_no("Do you really want to delete this entry/these entries?",title="You sure?"):
            _save_entries({
                i for n,i in enumerate(entries)
                if not n in v["Table"]
            })

            entries = list(_load_entries())
            w["Table"](_entries_to_table(entries))

        if e is None:
            w.close()
            return None



