""" SHEST GUI CLIENT """

from CONSTANTS import *
from cryptography.fernet import Fernet
import requests
from threading import Thread
import time
import tkinter


def load_key():
    """Load the previously generated key"""

    with open('secret.key', 'r') as file:
        return file.read()


def encrypt_message(message: str):
    """
    Encrypts a message"
    :param message: A regular message.
    :return: The encrypted message.
    """

    key = load_key()
    f = Fernet(key)
    message = message.encode()
    encrypted_message = f.encrypt(message)
    return encrypted_message


def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    :param encrypted_message: The encrypted message to decrypt.
    :return: The decrypted message.
    """

    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message


root = tkinter.Tk()
frame = tkinter.Frame(root)
command_inp = tkinter.Text(frame, width=70, height=1, fg="green")


def download(command: list):
    """
    Handle download commands
    :param command: A command given by the user.
    """

    file_name = command[1].split("\\")[-1]
    with requests.put(download_path, data=encrypt_message(file_name),
                      stream=True) as response:
        with open(command[1], 'w') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(decrypt_message(chunk).decode())

    for widget in frame.winfo_children():
        widget.destroy()
    output = tkinter.Label(frame, text=f"{file_name} has been downloaded "
                                       f"from the server!")
    output.grid(row=0, column=0)
    root.update()


def upload(command: list):
    """
    Handle upload commands
    :param command: A command given by the user.
    """

    counter = 1
    file_name = command[1].split("\\")[-1]
    with open(command[1], 'r') as file:
        for chunk in file:
            if counter == 1:
                requests.put(upload_path + f'{file_name}?q=w',
                             data=encrypt_message(chunk))
            else:
                requests.put(upload_path + f'{file_name}',
                             data=encrypt_message(chunk))
            counter += 1

    for widget in frame.winfo_children():
        widget.destroy()
    output = tkinter.Label(frame, text=f"{file_name}"
                                       f" has been uploaded to the server!")
    output.grid(row=0, column=0)
    root.update()


def regular(command: list):
    """
    Handle regular commands
    :param command: A command given by the user.
    """

    response = requests.put(regular_path,
                            data=encrypt_message(" ".join(command)))
    response = decrypt_message(response.content).decode()

    for widget in frame.winfo_children():
        widget.destroy()
    output = tkinter.Label(frame, text=f"output:\n{response}")
    output.grid(row=0, column=0)
    root.update()


def retrieve_input():
    """
    Get a command input from the user and get the output to the command
    from a fastapi server
    """

    command = command_inp.get("1.0", "end-1c").split(" ")
    if command[0] == 'download':
        download(command)

    elif command[0] == "upload":
        upload(command)

    else:
        regular(command)

    time.sleep(5)
    root.destroy()


def main():
    """ Configure client window and run it """

    frame.grid(row=0, column=0)
    title = tkinter.Label(frame, text=title_massage, font=(None, 15))
    title.grid(row=0, column=0)
    space1 = tkinter.Label(frame, text="\n")
    space1.grid(row=1, column=0)
    command_inp.grid(row=2, column=0)
    confirm = tkinter.Button(frame, text="execute",
                             command=lambda: retrieve_input())
    confirm.grid(row=2, column=1)
    space2 = tkinter.Label(frame, text="\n")
    space2.grid(row=3, column=0)
    root.mainloop()


if __name__ == '__main__':
    main()
