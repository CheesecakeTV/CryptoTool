from Crypto.PublicKey import ECC
from Crypto.Hash import SHAKE128
from Crypto.Protocol.DH import key_agreement
import FreeSimpleGUI as sg
from Crypto.PublicKey.ECC import EccKey
import base64
import clipboard as clp
from hashlib import shake_128

kdf = lambda a:SHAKE128.new(a).read(32)

def _get_layout() -> list[list[sg.Element]]:
    """
    Window layout
    :return:
    """
    layout = [
        [
            sg.T("Use this algorithm to create and transmit a secret \"password\".",size=(70,0))
        ],[
            #sg.T("Follow the steps below.")
        ],[
            sg.HSep()
        ],[
            sg.T("1. This text was copied to your clipboard. Send it to your partner:")
        ],[
            sg.In("",key="Public_Key",disabled=True,disabled_readonly_background_color="",font="Any 8",size=(95,0)),
        ],[
            sg.HSep()
        ],[
            sg.T("2. Paste the text received from your partner here:"),
        ],[
            sg.In(key="Partner_Key",font="Any 8",size=(95,0),enable_events=True),
            sg.Button("Paste",key="Paste_Key"),
        ],[
            sg.T("You pasted your own key... Paste the partners key instead!",key="PastedOwnKey",visible=False,text_color="red")
        ],[
            sg.HSep()
        ],[
            sg.T("3. Done!")
        ],[
            sg.T("If your partner has the same checksum, everything worked fine:")
        ],[
            sg.In(disabled=True,disabled_readonly_background_color="",size=(10,0),key="Checksum")
        ],[
            sg.Button("Done (Apply key)",key="Done"),
            sg.Button("Retry",key="Retry"),
            sg.Button("Save to file",key="Save_To_File",visible=False),
        ]
    ]

    return layout

def _retry(w,*_,encoder=base64.b16encode) -> EccKey:
    """
    Redo Key exchange
    :param w:
    :return:
    """
    myKey = ECC.generate(curve='Ed25519')

    encoded = encoder(myKey.public_key().export_key(format="DER"))

    w["Public_Key"](encoded.decode())
    clp.copy(encoded.decode())

    w["Partner_Key"]("")
    w["Checksum"]("")
    w["PastedOwnKey"].update(visible=False)

    return myKey

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
    w["Partner_Key"].bind("<Button-1>","_click")

    my_key = _retry(w)
    session_key = None

    while True:
        e,v = w.read()
        print(e)

        if e is None:
            w.close()
            return None

        if e == "Paste_Key" or (e == "Partner_Key_click" and not v["Partner_Key"]):
            _ = clp.paste().strip()
            if len(_) == 88:
                w["Partner_Key"](_)
                v["Partner_Key"] = _
                e = "Partner_Key"

        if e == "Partner_Key":
            _ = v["Partner_Key"].strip()

            if _ == v["Public_Key"]:
                w["PastedOwnKey"].update(visible=True)
            else:
                w["PastedOwnKey"].update(visible=False)

            if len(_) == 88:
                try:
                    session_key = key_agreement(static_priv=my_key, static_pub=ECC.import_key(base64.b16decode(_)), kdf=kdf)
                    w["Checksum"](base64.b16encode(shake_128(session_key).digest(3)))
                except ValueError:
                    w["Checksum"]("")
            else:
                w["Checksum"]("")

        if e == "Retry":
            _retry(w)
            session_key = None

        if e == "Done":
            w.close()
            return session_key


if __name__ == "__main__":
    print("Done:",perform_key_exchange())