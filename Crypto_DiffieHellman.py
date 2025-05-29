from Crypto.PublicKey import ECC
from Crypto.Hash import SHAKE128
from Crypto.Protocol.DH import key_agreement
import FreeSimpleGUI as sg

kdf = lambda a:SHAKE128.new(a).read(32)

def _get_layout() -> list[list[sg.Element]]:
    """
    Window layout
    :return:
    """
    layout = [
        [
            sg.T("Use this algorithm to create and transmit a secret \"password\".")
        ],[
            #sg.T("Follow the steps below.")
        ],[
            sg.HSep()
        ],[
            sg.T("1. Copy this text and send it to your partner:")
        ],[
            sg.In("",key="Public_Key",disabled=True,disabled_readonly_background_color="",expand_x=True),
            sg.Button("Copy",key="Copy_Key"),
        ],[
            sg.HSep()
        ],[
            sg.T("2. Paste the text received from your partner here:"),
        ],[
            sg.In(key="Partner_Key",expand_x=True),
            sg.Button("Paste",key="Paste_Key"),
        ],[
            sg.HSep()
        ],[
            sg.T("3. Done!")
        ],[
            sg.T("You both have the same, secure key now.")
        ],[
            sg.Button("Done",key="Done"),
            sg.Button("Retry",key="Retry",visible=False),
            sg.Button("Save to file",key="Save_To_File",visible=False),
        ]
    ]

    return layout

def perform_key_exchange() -> bytes|None:
    """
    Complete key exchange with UI and such
    :return:
    """
    sg.theme("DarkGray11")
    sg.set_options(font="Any 12")
    layout = _get_layout()

    w = sg.Window("Diffie-Hellman key exchange",layout,finalize=True)
    w.read(timeout=10)

    while True:
        e,v = w.read()

        if e is None:
            w.close()
            return None


if __name__ == "__main__":
    perform_key_exchange()