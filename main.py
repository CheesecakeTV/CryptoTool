import Crypto_full
import Crypto_files
import FreeSimpleGUI as sg
import base64
import clipboard as clp
from functools import partial
from pathlib import Path

def throw_event(w:sg.Window,event:str,value:any=None):
    """
    Throws an event
    :param w: Window to throw to
    :param event: Event name
    :param value: Event value
    :return:
    """
    w.write_event_value(event,value)

def _get_main_layout():
    """Main layout"""

    ### Abstractly called key-functions ###
    def paste_to_input_multiline(w,e,v):
        w["IN_Multiline"](clp.paste())
        throw_event(w,"IN_Multiline_CtrlReturn")


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
            sg.Multiline(key="IN_Multiline",size=_multiline_size,enable_events=True)
        ],[
            sg.Button("Refresh (Ctrl + Return)",key="Refresh_output"),
            sg.Button("Paste from clipboard",key=paste_to_input_multiline),
            sg.Button("Clear",key=lambda w,_,__:w["IN_Multiline"](""))
        ]
    ],key="IN_Text")

    tab_in_file = sg.Tab("File (WIP)",[ # Todo
        [
            sg.FileBrowse("Select file",target="IN_File_Path"),
            sg.In(key="IN_File_Path",enable_events=True,expand_x=True),
            sg.Button("En-/Decrypt",key="IN_File_Crypt")
        ]
    ],element_justification="center",key="IN_File")

    tab_in_clipboard = sg.Tab("Clipboard (WIP)",[ # Todo
        [
            sg.Button("Text from clipboard",key="Clipboard_Text",size=(_button_size:=(20,0))),
        ],[
            sg.Button("Image from clipboard", key="Clipboard_Image", size=_button_size),
        ]
    ],element_justification="center",key="IN_Clipboard")

    tab_in_email = sg.Tab("Mail (WIP)",[ # Todo
        [
            sg.T("WIP")
        ]
    ])

    tab_out_clipboard = sg.Tab("Clipboard (WIP)",[ # Todo
        [
            sg.Button("Text to clipboard",key="Clipboard_out_Text",size=(_button_size:=(20,0))),
        ],[
            sg.Button("Image to clipboard", key="Clipboard_out_Image", size=_button_size),
        ]
    ],element_justification="center",key="OUT_Clipboard")

    tab_out_multiline = sg.Tab("Text",[
        [
            sg.Multiline(key="OUT_Multiline",size=_multiline_size,disabled=True),
        ],[
            sg.Button("Copy to clipboard",key=lambda _,__,v:clp.copy(v["OUT_Multiline"])),
            sg.Checkbox("Automatically copy to clipboard",key="OUT_Multiline_AutoCopyCLP")
        ]
    ],key="OUT_Text")

    tab_out_tempfile = sg.Tab("Tempfile (WIP)",[
        [
            sg.Radio("View file",key="TMP_View_File",group_id="Tempfile"),
            sg.T("Ending:"),
            sg.In(key="TMP_View_File_Ending"),
        ]
    ],key="OUT_Tempfile") # Todo # File that gets opened once and deleted after

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
            sg.Frame("Encoding (Literal text)",frame_encoding,key="Encoding_Frame",vertical_alignment="top")
        ],[
            sg.Radio("Automatic",group_id="Direction",key="AutomaticDirection",default=True,enable_events=True),
            sg.Radio("Encrypt",group_id="Direction",key="Encrypt",enable_events=True),
            sg.Radio("Decrypt", group_id="Direction",key="Encrypt_false",enable_events=True),
            sg.T("",key="DecryptionStatus")
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

def bind_events(w,*_):
    """
    TKinter event-binding
    :param w:
    :param _:
    :return:
    """
    w["IN_Multiline"].bind("<Control-Return>","_CtrlReturn")

def get_input_text(w,e,v) -> bytes:
    """Multiline input"""
    return v["IN_Multiline"].strip().encode()

def get_input_file(w,e,v) -> bytes:
    """Single file"""
    path = Path(v["IN_File_Path"])

    if path.exists():
        return path.read_bytes()
    return b""

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
        # case "OUT_Text":
        #     data = data.decode()
        #     w["OUT_Multiline"](data)
        #     if v["OUT_Multiline_AutoCopyCLP"]:
        #         clp.copy(data)
        case "OUT_File":
            ...
        case "OUT_Clipboard":
            ...
        case "OUT_Tempfile":
            ...

def set_output_text(w,e,v,data:bytes):
    """Output in multiline text-field"""
    data = data.decode()

    if len(data) > 10000:
        set_encryption_status(w,e,v,"Output too long","orange")
        w["OUT_Multiline"]("")
        return

    w["OUT_Multiline"](data)
    if v["OUT_Multiline_AutoCopyCLP"]:
        clp.copy(data)

def get_encoder_decoder_text(_,__,v) -> tuple[callable, callable]:
    """
    Returns the selected encoder and decoder (Base64, Base16, etc.)
    :return: encoder, decoder
    """
    if v["ENC_Base16"]:
        return base64.b16encode,base64.b16decode

    if v["ENC_Base64"]:
        return base64.b64encode,base64.b64decode

def encrypt_text(w,e,v,data:bytes) -> bytes:
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

def decrypt_text(w,e,v,data:bytes,verify:bool=True) -> bytes:
    """
    Decrypts the data.
    Might be extended in the future
    :param verify: Will raise a ValueError if message was modified
    :param data:
    :param w:
    :param e:
    :param v:
    :return:
    """
    return Crypto_full.decrypt_full(get_password(w, e, v), data, verify=verify)

def set_encryption_status(w,e,v,status:str="Ready",bg_color:str="beige",txt_color:str="black"):
    """
    Modifies status text
    :param txt_color: Text color
    :param w:
    :param e:
    :param v:
    :param status: Status text
    :param bg_color: Background color
    :return:
    """
    w["DecryptionStatus"](status)
    w["DecryptionStatus"].update(background_color=bg_color)
    w["DecryptionStatus"].update(text_color=txt_color)

# Provide functions for each stage
pipeline_input:callable = get_input_text
pipeline_encoding:callable = base64.b64encode
pipeline_decoding:callable = base64.b64decode
pipeline_output:callable = set_output
pipeline_encrypt:callable = encrypt_text
pipeline_decrypt:callable = decrypt_text

def full_pipeline(w,e,v):
    """
    Handles the full encoding/decoding
    :param w:
    :param e:
    :param v:
    :return:
    """
    data_in:bytes = pipeline_input(w,e,v)

    if not data_in:
        set_encryption_status(w,e,v,status="No input",bg_color="DarkGray",txt_color="black")
        return

    if v["AutomaticDirection"]: # Automatic direction check
        try:
            # Decryption
            crypted_data = pipeline_decoding(data_in)
            crypted_data = pipeline_decrypt(w,e,v,crypted_data)
            set_encryption_status(w, e, v, status="Decrypted", bg_color="lime",txt_color="black")  # Reset alarm
        except ValueError:
            # Encryption
            crypted_data = pipeline_encrypt(w, e, v, data_in)
            crypted_data = pipeline_encoding(crypted_data)
            set_encryption_status(w, e, v, status="Encrypted", bg_color="LightSkyBlue", txt_color="black")

    elif v["Encrypt"]:  # Normal encryption
        crypted_data = pipeline_encrypt(w,e,v,data_in)
        crypted_data = pipeline_encoding(crypted_data)
        set_encryption_status(w,e,v,status="Encrypted",bg_color="LightSkyBlue",txt_color="black")
    else:
        crypted_data = b""  # So that the IDE doesn't complain
        try:
            crypted_data = pipeline_decoding(data_in)
            crypted_data = pipeline_decrypt(w, e, v, crypted_data)
            set_encryption_status(w, e, v, status="Decrypted", bg_color="lime",txt_color="black")  # Reset alarm
        except ValueError:
            try:
                crypted_data = pipeline_decrypt(w, e, v, crypted_data, verify=False)
                set_encryption_status(w, e, v, "Message might be modified!", bg_color="red", txt_color="lime")
            except ValueError:
                set_encryption_status(w,e,v,"Message has wrong format or is incomplete!",bg_color="orange", txt_color="black")
                crypted_data = b"Error"

    try:
        pipeline_output(w,e,v,crypted_data)
    except UnicodeDecodeError:
        set_encryption_status(w, e, v, "Wrong settings or password", bg_color="orange", txt_color="black")

def main():
    global pipeline_encoding,pipeline_decoding,pipeline_output,pipeline_input,pipeline_encrypt,pipeline_decrypt

    w = sg.Window("Cypher Tool",_get_main_layout(),finalize=True,element_justification="center")
    e,v = w.read(timeout=10)

    set_encryption_status(w,e,v)
    bind_events(w)

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
                try:
                    e(w,e,v,w[e])
                except (TypeError,KeyError):
                    e(w,e,v)
                continue
            except Exception as ex:
                print("Abstract call error:",ex.__class__.__name__,ex)

        ### Non-abstract functionality ###
        if e == "IN_Multiline":
            set_encryption_status(w,e,v)

        if v["IN_Type"] in ["IN_Text"] and e in ["IN_Type","ENC_Base16","ENC_Base64"]:
            match e:
                case "ENC_Base16":
                    pipeline_encoding = base64.b16encode
                    pipeline_decoding = base64.b16decode
                case "ENC_Base64":
                    pipeline_encoding = base64.b64encode
                    pipeline_decoding = base64.b64decode

        # Input
        temp_dict = {
            "IN_Text":get_input_text,
            #"IN_File":get_input_file
        }
        if v["IN_Type"] in temp_dict:
            pipeline_input = temp_dict[v["IN_Type"]]

        # Output
        temp_dict = {
            "OUT_Text":set_output_text,
            #"OUT_File":set_output_file
        }
        if v["OUT_Type"] in temp_dict:
            pipeline_output = temp_dict[v["OUT_Type"]]

        if e in ["IN_File_Crypt"]:
            pipeline_input = get_input_file
            full_pipeline(w,e,v)

        # Execute en-/decryption
        if e in ["Refresh_output","IN_Multiline_CtrlReturn"]:
            full_pipeline(w,e,v)


    print("Program closing")



if __name__ == '__main__':
    main()




