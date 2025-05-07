import Crypto_full
import Crypto_files
import FreeSimpleGUI as sg
import base64

def _get_main_layout():
    """Main layout"""
    _multiline_size = (80,15)

    _radio_args = {
        "group_id":"Encoding",
        "size":(10,0),
        "enable_events":True,
    }
    frame_encoding = [
        [sg.Radio("Base16", key="ENC_Base16", tooltip="Works for most chats",**_radio_args)],
        [sg.Radio("Base64",key="ENC_Base64",tooltip="Works for many chats and is smaller",default=True,**_radio_args)],
    ]

    tab_in_multiline = sg.Tab("Text",[
        [
            sg.Multiline(key="IN_Multiline",size=_multiline_size)
        ],[
            sg.Button("Refresh (Ctrl + enter)",key="Refresh_output"),
        ]
    ],key="IN_Text")

    tab_in_file = sg.Tab("File",[
        [
            sg.FileBrowse()
        ]
    ],element_justification="center",key="IN_File")

    tab_in_clipboard = sg.Tab("Clipboard",[
        [
            sg.Button("Text from clipboard",key="Clipboard_Text",size=(_button_size:=(20,0))),
        ],[
            sg.Button("Image from clipboard", key="Clipboard_Image", size=_button_size),
        ]
    ],element_justification="center",key="IN_Clipboard")

    tab_in_email = sg.Tab("Mail",[
        [
            sg.T("WIP")
        ]
    ])

    tab_out_clipboard = sg.Tab("Clipboard",[
        [
            sg.Button("Text to clipboard",key="Clipboard_out_Text",size=(_button_size:=(20,0))),
        ],[
            sg.Button("Image to clipboard", key="Clipboard_out_Image", size=_button_size),
        ]
    ],element_justification="center",key="OUT_Clipboard")

    tab_out_multiline = sg.Tab("Text",[
        [
            sg.Multiline(key="OUT_multiline",size=_multiline_size,disabled=True),
        ]
    ],key="OUT_Text")

    tab_out_tempfile = sg.Tab("Tempfile",[],key="OUT_Tempfile") # File that gets opened once and deleted after

    tab_password_Text = sg.Tab("Text",[
        [
            sg.In(key="password_text",size=(25,0),password_char="*"),
        ],[
            sg.Checkbox(
                "Show password",
                key=lambda w,e,v,self:self.update(w["password_text"].update(password_char="" if v[e] else "*")),
                enable_events = True,
            ),
        ]
    ],key="PW_Text")

    layout = [
        [
            sg.TabGroup([[tab_in_multiline,tab_in_file,tab_in_clipboard]],enable_events=True,key="IN_Type"),
            sg.Frame("Encoding",frame_encoding,key="Encoding_Frame",vertical_alignment="top")
        ],[
            sg.Radio("Encrypt",group_id="Direction",key="Encrypt",default=True,enable_events=True),
            sg.Radio("Decrypt", group_id="Direction",key="Encrypt_false",enable_events=True),
        ],[
            sg.TabGroup([[tab_out_multiline,tab_out_clipboard,tab_out_tempfile]],key="OUT_Type",expand_y=True,enable_events=True),
            sg.Frame("Password",
                     [[sg.TabGroup([[
                         tab_password_Text
                     ]],key="PW_Type")]],
                     expand_y=True,
            )
        ]
    ]

    return layout

def get_input(_,__,v) -> bytes:
    """
    "Reads" the current input
    :param _:
    :param __:
    :param v:
    :return:
    """
    match v["IN_Type"]:
        case "IN_Text":
            return v["IN_Multiline"].strip().encode()
        case "IN_File":
            ...
        case "IN_Clipboard":
            ...

def get_password(_,__,v) -> str:
    """
    Returns the current password
    :param _:
    :param __:
    :param v:
    :return:
    """
    match v["PW_Type"]:
        case "PW_Text":
            return v["password_text"]

def set_output(w,_,v,data:bytes) -> None:
    """
    Forwards the data to a set output
    :param v:
    :param _:
    :param w:
    :param data: En-/decrypted data to be output
    :return:
    """
    match v["OUT_Type"]:
        case "OUT_Text":
            w["OUT_multiline"](data.decode())
        case "OUT_File":
            ...
        case "OUT_Clipboard":
            ...
        case "OUT_Tempfile":
            ...

def get_encoder_decoder(_,__,v) -> tuple[callable, callable]:
    """
    Returns the selected encoder and decoder (Base64, Base16, etc.)
    :return: encoder, decoder
    """
    # if v["ENC_Plain"]: # Not necessary, since you can't display all those chars anyways
    #     temp = lambda a:a
    #     return temp, temp

    if v["ENC_Base16"]:
        return base64.b16encode,base64.b16decode

    if v["ENC_Base64"]:
        return base64.b64encode,base64.b64decode

def encrypt(w,e,v,data:bytes) -> bytes:
    """
    Encrypts the data.
    Might be extended in the future
    :param data:
    :param w:
    :param e:
    :param v:
    :return:
    """
    return Crypto_full.encrypt_full(get_password(w,e,v),data)

def decrypt(w,e,v,data:bytes) -> bytes:
    """
    Encrypts the data.
    Might be extended in the future
    :param data:
    :param w:
    :param e:
    :param v:
    :return:
    """
    return Crypto_full.decrypt_full(get_password(w, e, v), data)

def full_pipeline(w,e,v):
    """
    Handles the full encoding/decoding
    :param w:
    :param e:
    :param v:
    :return:
    """
    data_in:bytes = get_input(w,e,v)

    if not data_in:
        return

    if v["Encrypt"]:
        crypted_data = encrypt(w,e,v,data_in)
        crypted_data = get_encoder_decoder(w,e,v)[0](crypted_data)
    else:
        crypted_data = get_encoder_decoder(w,e,v)[1](data_in)
        crypted_data = decrypt(w,e,v,crypted_data)

    set_output(w,e,v,crypted_data)


def main():

    w = sg.Window("Cypher Tool",_get_main_layout(),finalize=True,element_justification="center")
    w.read(timeout=10)

    while True:
        e,v = w.read()

        if e is None:
            w.close()
            break

        ### Abstract ###

        if e in v:
            print(e,v[e])
        else:
            print(e)

        if callable(e):
            try:
                e(w,e,v,w[e])
            except (TypeError,KeyError):
                e(w,e,v)
            continue

        ### Non-abstract functionality ###
        if e == "Refresh_output":
            full_pipeline(w,e,v)


    print("Program closing")



if __name__ == '__main__':
    main()




