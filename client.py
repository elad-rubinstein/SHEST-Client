""" Shest Gui Client """


from CONSTANTS import DOWNLOAD_PATH, UPLOAD_PATH, REGULAR_PATH, \
    DOWNLOAD_COMMAND, UPLOAD_COMMAND, KEY
from cryptography.fernet import Fernet
from pathlib import Path
from re import search
import requests
import time
import tkinter
from typing import List


def window_configuration() -> None:
    """ Configure the main client tkinter window """

    root = tkinter.Tk()
    frame = tkinter.Frame(root)
    command_inp = tkinter.Text(frame, width=70, height=1, fg="green")
    frame.grid(row=0, column=0)
    title = tkinter.Label(frame, text="Hy there! Please type a command and I "
                                      "will execute it for you:\nupload: upload"
                                      " <path>\ndownload: download <path>",
                          font=(None, 15))
    title.grid(row=0, column=0)
    space1 = tkinter.Label(frame, text="\n")
    space1.grid(row=1, column=0)
    command_inp.grid(row=2, column=0)
    confirm = tkinter.Button(frame, text="execute",
                             command=lambda: retrieve_input(command_inp, frame))
    confirm.grid(row=2, column=1)
    space2 = tkinter.Label(frame, text="\n")
    space2.grid(row=3, column=0)
    root.mainloop()


def encrypt_message(message: str) -> bytes:
    """
    Encrypt a message

    :param message: A regular message.
    :return: The encrypted message.
    """

    f = Fernet(KEY)
    message = message.encode()
    encrypted_message = f.encrypt(message)
    return encrypted_message


def decrypt_message(encrypted_message: bytes) -> str:
    """
    Decrypt an encrypted message

    :param encrypted_message: The encrypted message to decrypt.
    :return: The decrypted message.
    """

    f = Fernet(KEY)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message


def download_conf(frame: tkinter.Frame, file_name: str) -> None:
    """
    Reconfigure the client window after the download command was executed

    :param frame: The main frame.
    :param file_name: The downloaded file name.
    """

    for widget in frame.winfo_children():
        widget.destroy()
    output = tkinter.Label(frame, text=f"{file_name} has been downloaded "
                                       f"from the server!")
    output.grid(row=0, column=0)
    root.update()


def upload_conf(frame: tkinter.Frame, file_name: str) -> None:
    """
    Reconfigure the client window after the upload command was executed

    :param frame: The main frame.
    :param file_name: The uploaded file name.
    """

    for widget in frame.winfo_children():
        widget.destroy()
    output = tkinter.Label(frame, text=f"{file_name}"
                                       f" has been uploaded to the server!")
    output.grid(row=0, column=0)
    root.update()


def regular_conf(frame: tkinter.Frame, output: str) -> None:
    """
    Reconfigure the client window according to a given output
    after a regular command was executed

    :param frame: The main frame.
    :param output: An output of a command.
    """

    for widget in frame.winfo_children():
        widget.destroy()
    output = tkinter.Label(frame, text=f"output:\n{output}")
    output.grid(row=0, column=0)
    root.update()


def run_download_command(command: List[str], frame: tkinter.Frame) -> None:
    """
    Handle download commands by passing the file's content to a shest server

    :param command: A command given by the user.
    :param frame: A frame for the client window configurations.
    """

    file_name = search("[a-zA-Z1-9]*\.[a-z]*", command[1]).group()
    with requests.put(DOWNLOAD_PATH, data=encrypt_message(file_name),
                      stream=True) as response:
        with Path(command[1], 'w').open() as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(decrypt_message(chunk).decode())

    download_conf(frame, file_name)


def run_upload_command(command: List[str], frame: tkinter.Frame) -> None:
    """
    Handle upload commands by passing the file's content to a shest server

    :param command: A command given by the user.
    :param frame: A frame for the client window configurations.
    """

    counter = 1
    file_name = search("[a-zA-Z1-9]*\.[a-z]*", command[1]).group()
    with Path(command[1], 'r').open() as file:
        for chunk in file:
            if counter == 1:
                requests.put(UPLOAD_PATH + f'{file_name}?q=w',
                             data=encrypt_message(chunk))
            else:
                requests.put(UPLOAD_PATH + f'{file_name}',
                             data=encrypt_message(chunk))
            counter += 1

    upload_conf(frame, file_name)


def run_regular_commands(command: List[str], frame: tkinter.Frame) -> None:
    """
    Handle regular commands by getting the output of the given them
    from a remote shest server

    :param command: A command given by the user.
    :param frame: A frame for the client window configurations.
    """

    response = requests.put(REGULAR_PATH,
                            data=encrypt_message(" ".join(command)))
    output = decrypt_message(response.content).decode()

    regular_conf(frame, output)


def retrieve_input(inp_textbox: tkinter.Text, frame: tkinter.Frame) -> None:
    """
    Get a command input from the user and get the output to the command
    from a fastapi server

    :param inp_textbox: A textbox for the command input.
    :param frame: A frame for the client window configurations.
    """

    command = inp_textbox.get("1.0", "end-1c").split(" ")
    mapper = {DOWNLOAD_COMMAND: run_download_command,
              UPLOAD_COMMAND: run_upload_command}
    if command[0] in mapper.keys():
        mapper[command[0]](command, frame)
    else:
        run_regular_commands(command, frame)
    time.sleep(5)
    root.destroy()


def main() -> None:
    """ Run the client window configuration method """

    window_configuration()


if __name__ == '__main__':
    main()
