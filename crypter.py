import PySimpleGUI as sg, os, base64, pyperclip
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet







sg.theme('DarkBrown1')

menu_def = [['&Edit',['Copy', 'Paste', 'E&xit']],
            ['&Help', '&About...']]

  
layout = [[sg.Menu(menu_def, tearoff=True)],
          [sg.Text('Encrypt and decrypt files', size=[40, 1])],      
          [sg.Output(size=(60, 20), key='out')],
          [sg.Text('Key',size=(10,1)),sg.In(size=(50,1), key=('key'))],
          [sg.Text('Password',size=(10,1)),sg.In(size=(50,1), key=('pass'))],
          [sg.Text('Select file', size=(10,1)),sg.In(size=(41, 1),key='-in-'), sg.FileBrowse()],
          [sg.Button('Encrypt'), sg.Button('Decrypt')]]


window = sg.Window('Crypter', default_element_size=(30, 2)).Layout(layout)      

while True:
    button, value = window.Read()
    filename = value['-in-']
    passw = value['pass']
    key = value['key']
    key1 = key.encode()
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
    file = open('key', 'rb')
    keyt = file.read() 
    file.close()
    if button == 'Encrypt':
        with open(filename, 'wb') as f:
            f.write(encrypted)
        with open("key", "wb") as ekey:
            ekey.write(key)
        
        print('File encrypted...')
        print('Key: ', c)


    elif button == 'Decrypt':
        key2 = keyt+key1
        fernet = Fernet(key2)
        encrypted = fernet.decrypt(data)
        with open(filename, 'wb') as f:
            f.write(encrypted)

        print('File decrypted... ')

    elif button == 'Copy':
        c = keyt.decode()
        pyperclip.copy(str(c))

    elif button == 'Paste':
        text = pyperclip.paste()
        window.Element('key').Update(str(text))
    

    elif button == 'About...':      
        sg.popup('About:', 'Created by A. Petek', 'Crypter', 'Version 1.0',)


    elif button == 'Exit':
        break
    
