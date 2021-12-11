#python file encryptor and decryptor
import PySimpleGUI as sg
import os
import base64
import webbrowser
from json import (load as jsonload, dump as jsondump)
from os import path
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


SETTINGS_FILE = path.join(path.dirname(__file__), r'settings_file.cfg')
DEFAULT_SETTINGS = {'theme': sg.theme()}
SETTINGS_KEYS_TO_ELEMENT_KEYS = {'theme': '-THEME-'}

def load_settings(settings_file, default_settings):
    try:
        with open(settings_file, 'r') as f:
            settings = jsonload(f)
    except Exception as e:
        sg.popup_quick_message(f'exception {e}', 'No settings file found... will create one for you', keep_on_top=True, background_color='red', text_color='white')
        settings = default_settings
        save_settings(settings_file, settings, None)
    return settings


def save_settings(settings_file, settings, values):
    if values:      
        for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:  
            try:
                settings[key] = values[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]]
            except Exception as e:
                print(f'Problem updating settings from window values. Key = {key}')

    with open(settings_file, 'w') as f:
        jsondump(settings, f)

    sg.popup('Settings saved')

def create_settings_window(settings):
    sg.theme(settings['theme'])

    def TextLabel(text): return sg.Text(text+':', justification='r', size=(15,1))

    layout = [  [sg.Text('Settings', font='Any 15')],
                [TextLabel('Theme'),sg.Combo(sg.theme_list(), size=(20, 20), key='-THEME-')],
                [sg.Button('Save'), sg.Button('Exit')]  ]

    window = sg.Window('Settings', layout, keep_on_top=True, finalize=True)

    for key in SETTINGS_KEYS_TO_ELEMENT_KEYS:
        try:
            window[SETTINGS_KEYS_TO_ELEMENT_KEYS[key]].update(value=settings[key])
        except Exception as e:
            print(f'Problem updating PySimpleGUI window from settings. Key = {key}')

    return window




        
def create_main_window(settings):
    sg.theme(settings['theme'])
    menu_def = [['&Menu', ['&Settings', 'E&xit']],
                ['&Help', '&About...']]

    right_click_menu = ['Unused', ['&Copy', '&Paste','Settings', 'E&xit']]

    layout =  [[sg.Menu(menu_def)],
               [sg.Image('enc.png'),sg.Text('Encrypt and decrypt files', size=[21, 1]), sg.Button('', key='paypal', size=(12,1), font=('Helvetica', 9), button_color=(sg.theme_background_color(), sg.theme_background_color()),
                           image_filename='paypal.png', image_size=(80, 50), image_subsample=2, border_width=0),
                 sg.Button('', key='bitcoin', size=(12,1), font=('Helvetica', 9), button_color=(sg.theme_background_color(), sg.theme_background_color()),
                           image_filename='bitcoin.png', image_size=(80, 60), image_subsample=2, border_width=0)],         
               [sg.Output(size=(60, 20), key='out')],
               [sg.Text('Password',size=(10,1)),sg.In(size=(49,1), key=('pass'))],
               [sg.Text('Select file', size=(10,1)),sg.In(size=(40, 1),key='-in-'), sg.FileBrowse()],
               [sg.Button('Encrypt'), sg.Button('Decrypt')]]

    return sg.Window('Crypter', default_element_size=(11, 2)).Layout(layout)      

def main():
    window, settings = None, load_settings(SETTINGS_FILE, DEFAULT_SETTINGS )
    while True:
        if window is None:
            window = create_main_window(settings)

        event, value = window.Read()
        filename = value['-in-']
        passw = value['pass']
        if event in (None, 'Exit'):
            break

        elif event == 'Encrypt':
            try:
                with open(filename, 'rb') as f:
                    data = f.read()
                salt = os.urandom(32)
                kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
                password = passw.encode()
                file = filename.encode()
                key = base64.urlsafe_b64encode(kdf.derive(password))
                c = key.decode()
                fernet = Fernet(key)
                encrypted = fernet.encrypt(data)
                file = open('key.docx', 'rb')
                keyt = file.read() 
                file.close()
                with open(filename, 'wb') as f:
                    f.write(encrypted)
                with open("key.docx", "wb") as ekey:
                    ekey.write(key)

                print('File encrypted...\n')
                print("Key is stored in key.docx file. Keep this in someplace safe! \nIf you lose it you’ll no longer be able to decrypt files.\n")
                print('Key: ', c)
            except FileNotFoundError:
                continue


        elif event == 'Decrypt':
            try:
                with open(filename, 'rb') as f:
                    data = f.read()
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
                password = passw.encode()
                file = filename.encode()
                key = base64.urlsafe_b64encode(kdf.derive(password))
                c = key.decode()
                fernet = Fernet(key)
                encrypted = fernet.encrypt(data)
                file = open('key.docx', 'rb')
                keyt = file.read() 
                file.close()
                fernet = Fernet(keyt)
                encrypted = fernet.decrypt(data)
                with open(filename, 'wb') as f:
                    f.write(encrypted)

                print('File decrypted... ')
            except FileNotFoundError:
                continue


        elif event == 'About...':
            sg.popup('About:', 'Created by A. Petek', 'Crypter', 'Version 1.1',)

        elif event == 'paypal':
            webbrowser.open_new_tab("https://www.paypal.com/donate/?cmd=_s-xclick&hosted_button_id=PFB6A6HLAQHC2&source=url")
        
        elif event == 'bitcoin':
            webbrowser.open_new_tab("https://commerce.coinbase.com/checkout/149a6235-ec7e-4d3b-a1ae-b08c4f08b4f6")
        
        elif event == 'Settings':
            event, values = create_settings_window(settings).read(close=True)
            if event == 'Save':
                window.close()
                window = None
                save_settings(SETTINGS_FILE, settings, values)

    window.Close()

main()
