import Crypto_full
import Crypto_files
import FreeSimpleGUI as sg
import base64


def main():

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

    tab_in_multiline = sg.Tab("Big input",[
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

    tab_out_tempfile = None # File that gets opened once and deleted after

    layout = [
        [
            sg.TabGroup([[tab_in_multiline,tab_in_file,tab_in_clipboard]]),
            sg.Frame("Encoding",frame_encoding,key="Encoding_Frame",vertical_alignment="top")
        ],[
            sg.Radio("Encrypt",group_id="Direction",key="Encrypt",default=True,enable_events=True),
            sg.Radio("Decrypt", group_id="Direction",key="Encrypt_false",enable_events=True),
        ]
    ]

    w = sg.Window("Cypher Tool",layout,finalize=True,element_justification="center")
    w.read(timeout=10)

    while True:
        e,v = w.read()
        print(v)

        if e is None:
            w.close()
            break

    print("Program complete")



if __name__ == '__main__':
    main()




