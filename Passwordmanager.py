from collections.abc import Iterable
from functools import total_ordering
from Globals import appdata
from dataclasses import dataclass,field
import FreeSimpleGUI as sg
import pickle
from datetime import datetime as dt
from Crypto_full import encrypt_full,decrypt_full
from typing import Self

manager_data = appdata / "Passwordmanager.pm"
_password: str | None = None
security_multiplier = 3

@total_ordering
@dataclass
class Entry:
    Title:str       # More of a group name
    Subtitle:str=""    # Specified usage
    Created:dt=field(default_factory=dt.now)  # Time created
    data:dict=field(default_factory=dict)

    def __hash__(self):
        return hash((self.Title.casefold(),self.Subtitle.casefold()))

    def __eq__(self, other:Self):
        return hash(self) == hash(other)

    def __lt__(self, other:Self):
        return self.Title < other.Title

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
                                   "\nAttention!\nIf you forget the password,\nyou can't access the passwordmanager\nwithout deleting all saved entries."
                                   , title="Setup Password", font="Any 12",keep_on_top=True,password_char="*")

        if not answer:
            return None

        sg.theme("DarkGray11")
        if answer != sg.popup_get_text("Please Repeat password:", font="Any 12", keep_on_top=True, password_char="*"):
            sg.popup_error("Entered passwords do not match!",font="Any 12")
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

def _load_entries() -> list[Entry]:
    """
    Returns saved passwords
    :return:
    """
    if _get_password() is None:
        return list()

    return sorted(list(pickle.loads(
        decrypt_full(
            _password,
            manager_data.read_bytes(),
            security_multiplier=security_multiplier
        )
    )))

def _save_entries(entries:list[Entry]):
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
            sg.Button("Delete",key="Delete"),
            sg.Button("Rename",key="Rename"),
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

def get_title_and_subtitle(window_title:str,title:str="", subtitle:str="") -> tuple[str,str]:
    """
    Title and subtitle window
    :param window_title:
    :param title:
    :param subtitle:
    :return: Title, subtitle
    """
    layout = [
        [
            sg.T("Title:",size=(10,0)),
            sg.In(title,key="Title")
        ],[
            sg.T("Subtitle:",size=(10,0)),
            sg.In(subtitle,key="Subtitle")
        ],[
            sg.Button("Save")
        ]
    ]

    w = sg.Window(window_title,layout,finalize=True)
    w.read(timeout=10)
    w["Title"].bind("<Return>","")
    w["Subtitle"].bind("<Return>","")
    e,v = w.read()

    if e is None:
        return "",""

    v = v.copy()
    w.close()

    title = v["Title"].strip()
    subtitle = v["Subtitle"].strip()

    return title, subtitle


def new_entry(data:dict) -> bool:
    """
    Create a new password-entry
    :param data:
    :return:
    """

    if _get_password() is None:
        return False

    title, subtitle = get_title_and_subtitle("New entry")

    if not title + subtitle:
        return False

    entries:set[Entry] = set(_load_entries())
    entries.add(Entry(title,subtitle,data=data))
    _save_entries(list(entries))

    return True

def passwordmanager() -> dict|None:
    """
    Full passwordmanager.
    Returns password-data if it is supposed to be opened
    :return:
    """
    sg.theme("DarkGray11")

    entries:list[Entry] = _load_entries()
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
            _save_entries([
                i for n,i in enumerate(entries)
                if not n in v["Table"]
            ])

            entries = _load_entries()
            w["Table"](_entries_to_table(entries))

        if e == "Rename" and v["Table"]:
            the_entry = entries[v["Table"][0]]

            new_title, new_subtitle = get_title_and_subtitle("Rename entry", the_entry.Title, the_entry.Subtitle)

            if not new_title + new_subtitle:
                continue

            the_entry.Title = new_title
            the_entry.Subtitle = new_subtitle

            _save_entries(entries)

            entries = _load_entries()
            w["Table"](_entries_to_table(entries))

        if e is None:
            w.close()
            return None


if __name__ == "__main__":
    passwordmanager()

