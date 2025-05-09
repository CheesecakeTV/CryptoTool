import os

from optree.functools import partial

import Crypto_full
import Crypto_files
import FreeSimpleGUI as sg
import base64
import clipboard as clp
from pathlib import Path
from enum import Enum

import Crypto_tempfiles

sg.theme("DarkGray11")

class DIRECTION(Enum):
    ENCRYPT = 1
    DECRYPT = 2
    AUTO = 3

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
            sg.Button("Refresh (Ctrl + Return)",key="IN_Text_Refresh_Output"),
            sg.Button("Paste from clipboard",key=paste_to_input_multiline),
            sg.Button("Clear",key=lambda w,_,__:w["IN_Multiline"](""))
        ]
    ],key="IN_Text")

    tab_in_file = sg.Tab("File",[
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
    ],element_justification="center",key="IN_Clipboard",visible=False)

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
    ],element_justification="center",key="OUT_Clipboard",visible=False)

    tab_out_multiline = sg.Tab("Text",[
        [
            sg.Multiline(key="OUT_Multiline",size=_multiline_size,disabled=True),
        ],[
            sg.Button("Copy to clipboard",key=lambda _,__,v:clp.copy(v["OUT_Multiline"])),
            sg.Checkbox("Automatically copy to clipboard",key="OUT_Multiline_AutoCopyCLP")
        ]
    ],key="OUT_Text")

    tab_out_file = sg.Tab("File",[
        [
            sg.FolderBrowse("Browse folder",target="OUT_File_BrowseFolder"),
            sg.In(key="OUT_File_BrowseFolder",enable_events=True,expand_x=True),
            sg.Button("Oben in Explorer",key=lambda w,e,v:os.system(f"start {Path(v['OUT_File_BrowseFolder']) if v['OUT_File_BrowseFolder'] else os.getcwd()}"))
        ]
    ],key="OUT_File")

    tab_out_tempfile = sg.Tab("Tempfile",[
        [
            sg.T("The file will be saved, opened and deleted after 5 minutes.\nIt will also be deleted once you close the program or reboot.")
            # sg.Radio("View file",key="TMP_View_File",group_id="Tempfile",default=True),
            # sg.T("Ending:"),
            # sg.In(key="TMP_View_File_Ending"),
        ],[
            sg.T("When encrypting, the folder will open so you can access the file.")
        ],[
            sg.Checkbox("Alyways open folder instead of file",key="OUT_Tempfile_AlwaysOpenFolder",default=False)
        ]
    ],key="OUT_Tempfile")

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
            sg.TabGroup([[tab_out_multiline,tab_out_file,tab_out_clipboard,tab_out_tempfile]],key="OUT_Type",expand_y=True,enable_events=True),
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
    pipeline_additional_data["Filename"] = "Message.txt"
    return v["IN_Multiline"].strip().encode()

def get_input_file(w,e,v) -> bytes:
    """Single file"""
    global pipeline_direction

    path = Path(v["IN_File_Path"])
    print(path.name)
    if not path.exists():
        return b""

    if (pipeline_direction == DIRECTION.ENCRYPT
            or (pipeline_direction == DIRECTION.AUTO and not path.name.endswith(".secret"))): # Read and put filename in front
        pipeline_direction = DIRECTION.ENCRYPT
        pipeline_additional_data["Filename"] = path.name
    else: # Only read
        pipeline_direction = DIRECTION.DECRYPT

    return path.read_bytes()

def decode_file(data:bytes) -> bytes:
    """Extract file-data"""
    if pipeline_direction == DIRECTION.DECRYPT and pipeline_additional_data.get("Files"):
        data,pipeline_additional_data["Filename"] = Crypto_files.get_data_and_filename(data)

    return data

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

def set_output_text(w,e,v,data:bytes):
    """Output in multiline text-field"""
    data = data.decode()

    if len(data) > 1000000:
        set_encryption_status(w,e,v,"Output too long","orange")
        w["OUT_Multiline"]("")
        return

    w["OUT_Multiline"](data)
    if v["OUT_Multiline_AutoCopyCLP"]:
        clp.copy(data)

def set_output_file(w,e,v,data:bytes,tempfile:bool=False):
    """Output for single file or tempfile"""

    try:
        if pipeline_direction == DIRECTION.DECRYPT:
            file_data, file_name = Crypto_files.get_data_and_filename(data)

            name_path = Path(file_name)
            if (not "." in file_name) or len(name_path.parts) > 1:
                # Data doesn't seem to be in the file-format
                name_path = Path("Message.txt")
                file_data = data

            if tempfile:
                if name_path.name.endswith(".secret"):
                    v["OUT_Tempfile_AlwaysOpenFolder"] = True   # Yeah, I know...

                Crypto_tempfiles.view_file_for_time(file_data,name_path.name,open_folder=v["OUT_Tempfile_AlwaysOpenFolder"])    # Todo: Add way to change duration
                return

            path = Path(v["OUT_File_BrowseFolder"]) / name_path
            try:
                path.write_bytes(file_data)
            except FileNotFoundError:
                (Path(v["OUT_File_BrowseFolder"]) / Path("Message.txt")).write_bytes(data)
        else:
            name_path = Path(Crypto_files.get_random_filename(32) + ".secret")

            if tempfile:
                Crypto_tempfiles.view_file_for_time(data,name_path.name,open_folder=True)
                return

            path = Path(v["OUT_File_BrowseFolder"]) / name_path
            path.write_bytes(data)
    except PermissionError:
        set_encryption_status(w,e,v,"Permission error!","red")

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

def encrypt_file(w,e,v,data:bytes) -> bytes:
    """Append some filename in case none is included already"""
    name = pipeline_additional_data.get("Filename","message.txt")
    return encrypt_text(w,e,v,chr(len(name)).encode() + name.encode() + data)

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
pipeline_encrypt:callable = encrypt_text
pipeline_decrypt:callable = decrypt_text
pipeline_output:callable = set_output_text

pipeline_direction:DIRECTION = DIRECTION.AUTO
pipeline_additional_data:dict = dict()  # Can be used to transfer some more parameters via the pipeline

def full_pipeline(w,e,v):
    """
    Handles the full encoding/decoding
    :param w:
    :param e:
    :param v:
    :return:
    """
    global pipeline_direction
    global pipeline_additional_data
    pipeline_additional_data = dict()

    if v["AutomaticDirection"]:
        pipeline_direction = DIRECTION.AUTO
    elif v["Encrypt"]:
        pipeline_direction = DIRECTION.ENCRYPT
    else:
        pipeline_direction = DIRECTION.DECRYPT

    data_in:bytes = pipeline_input(w,e,v)

    if not data_in:
        set_encryption_status(w,e,v,status="No input",bg_color="DarkGray",txt_color="black")
        return

    if pipeline_direction == DIRECTION.AUTO: # Automatic direction check
        try:
            # Decryption
            pipeline_direction = DIRECTION.DECRYPT
            crypted_data = pipeline_decoding(data_in)
            crypted_data = pipeline_decrypt(w,e,v,crypted_data)
            set_encryption_status(w, e, v, status="Decrypted", bg_color="lime",txt_color="black")  # Reset alarm
        except ValueError:
            # Encryption
            pipeline_direction = DIRECTION.ENCRYPT
            crypted_data = pipeline_encrypt(w, e, v, data_in)
            crypted_data = pipeline_encoding(crypted_data)
            set_encryption_status(w, e, v, status="Encrypted", bg_color="LightSkyBlue", txt_color="black")

    elif pipeline_direction == DIRECTION.ENCRYPT:  # Normal encryption
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

        print(e)
        # if e in v:
        #     print(e,v[e])
        # else:
        #     print(e)

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
        if e in ["IN_Multiline","IN_File_Path"]:
            set_encryption_status(w,e,v)

        if v["OUT_Type"] in ["OUT_Text"]:
            pipeline_encrypt = encrypt_text

            if v["ENC_Base16"]:
                pipeline_encoding = base64.b16encode
            elif v["ENC_Base64"]:
                pipeline_encoding = base64.b64encode
        elif v["OUT_Type"] in ["OUT_File","OUT_Tempfile"]:
            pipeline_encrypt = encrypt_file
            pipeline_encoding = lambda a:a
        else:
            pipeline_encoding = lambda a:a

        if v["IN_Type"] in ["IN_Text"]:
            if v["ENC_Base16"]:
                pipeline_decoding = base64.b16decode
            elif v["ENC_Base64"]:
                pipeline_decoding = base64.b64decode
        elif v["IN_Type"] == "IN_File":
            pipeline_decoding = decode_file
        else:
            pipeline_decoding = lambda a:a

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
            "OUT_File":set_output_file,
            "OUT_Tempfile":partial(set_output_file,tempfile=True)
        }
        if v["OUT_Type"] in temp_dict:
            pipeline_output = temp_dict[v["OUT_Type"]]

        if e in ["IN_File_Crypt"] and v["IN_File_Path"]:
            pipeline_input = get_input_file
            full_pipeline(w,e,v)

        # Execute en-/decryption
        if e in ["IN_Text_Refresh_Output","IN_Multiline_CtrlReturn"]:
            full_pipeline(w,e,v)


    print("Program closing")



if __name__ == '__main__':
    main()




