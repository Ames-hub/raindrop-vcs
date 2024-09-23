from cryptography.fernet import Fernet
import cryptography.fernet
import datetime
import logging
import os

logging.basicConfig(
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s'
)

class encryption:
    def __init__(self, key_file='private.key'):
        self.key_file = key_file
        if not os.path.exists(key_file):
            self.generate_key()
        self.fernet_key = self.get_key()
        try:
            self.fernet = Fernet(self.fernet_key)
        except ValueError:
            err_msg = (
                "The key file is empty or has been tampered with. Your data may be at risk.\n"
                "As it has been changed and if you yourself did not change it, this is a sign of a security breach.\n"
                "If you yourself did not change it, you should consider changing the key file and re-encrypting your data.\n"
                "If you did change it, please change it back to the original key file or re-encrypt your data with the new key.\n\n"
                "The program will remain broken until this is resolved.\n"
                "(in an emergency, you can delete the secret.key file and the settings.json and our PostgreSQL DB Container and it will be regenerated)"
            )
            print(err_msg)
            logging.error(err_msg)

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as key_file:
            key_file.write(key)

    def get_key(self) -> bytes:
        with open(self.key_file, 'rb') as key_file:
            return key_file.read()

    def encrypt(self, message):
        encoded_message = message.encode('utf-8')
        try:
            encrypted_message = self.fernet.encrypt(encoded_message)
            return encrypted_message.decode('utf-8')
        except cryptography.fernet.InvalidToken:
            err_msg = "Invalid token. The message may have been tampered with or you may be using the wrong private.key file."
            print(err_msg)
            logging.error(err_msg)
        except ValueError:
            err_msg = "The message is empty or the key has been tampered with."
            print(err_msg)
            logging.error(err_msg)

    def decrypt(self, encrypted_message):
        encrypted_message_bytes = encrypted_message.encode('utf-8')
        try:
            decrypted_message = self.fernet.decrypt(encrypted_message_bytes)
            return decrypted_message.decode('utf-8')
        except cryptography.fernet.InvalidToken:
            err_msg = "Invalid token. The message may have been tampered with or you may be using the wrong private.key file."
            print(err_msg)
            logging.error(err_msg)
        except ValueError:
            err_msg = "The message is empty or the key has been tampered with."
            print(err_msg)
            logging.error(err_msg)
