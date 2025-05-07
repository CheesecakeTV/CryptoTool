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
            sg.Multiline(key="in_multiline",size=_multiline_size)
        ]
    ])

    tab_in_file = sg.Tab("File",[
        [
            sg.FileBrowse()
        ]
    ],element_justification="center")

    tab_in_clipboard = sg.Tab("Clipboard",[
        [
            sg.Button("Text from clipboard",key="Clipboard_Text",size=(_button_size:=(20,0))),
        ],[
            sg.Button("Image from clipboard", key="Clipboard_Image", size=_button_size),
        ]
    ],element_justification="center")

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
    ],element_justification="center")

    tab_out_multiline = sg.Tab("Text",[
        [
            sg.Multiline(key="out_multiline",size=_multiline_size)
        ]
    ])

    tab_out_tempfile = sg.Tab("Tempfile",[]) # File that gets opened once and deleted after

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
    ])

    layout = [
        [
            sg.TabGroup([[tab_in_multiline,tab_in_file,tab_in_clipboard]]),
            sg.Frame("Encoding",frame_encoding,key="Encoding_Frame",vertical_alignment="top")
        ],[
            sg.Radio("Encrypt",group_id="Direction",key="Encrypt",default=True,enable_events=True),
            sg.Radio("Decrypt", group_id="Direction",key="Encrypt_false",enable_events=True),
        ],[
            sg.TabGroup([[tab_out_multiline,tab_out_clipboard,tab_out_tempfile]],expand_y=True),
            sg.Frame("Password",
                     [[sg.TabGroup([[tab_password_Text]])]],
                     expand_y=True
            )
        ]
    ]

    return layout


def main():

    w = sg.Window("Cypher Tool",_get_main_layout(),finalize=True,element_justification="center")
    w.read(timeout=10)

    while True:
        e,v = w.read()
        print(v)

        if e is None:
            w.close()
            break

        if callable(e):
            try:
                e(w,e,v,w[e])
            except (TypeError,KeyError):
                e(w,e,v)
            continue

    print("Program complete")



if __name__ == '__main__':
    main()




