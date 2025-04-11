from hashlib import sha256
from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from .singleton_meta import SingletonMeta


class PrivateKey(metaclass=SingletonMeta):
    """
    A class for managing the private key.
    Only one instance of the class can exist throughout the application.
    """

    def __init__(self):
        self.__private_key = None

    def load_private_key(self, private_key_path: str, pin: str) -> None:
        """
        Loads the private key from the specified path and decrypts it with the specified PIN.
        Uses SHA-256 to hash the PIN before usage.
        :param:
            private_key_path: The path to the private key file.
            pin: A PIN to decrypt the private key.
        """
        hashed_pin = sha256(pin.encode()).digest()
        with open(private_key_path, "rb") as f:
            try:
                self.__private_key = serialization.load_pem_private_key(
                    f.read(), password=hashed_pin
                )
                print("private key was loaded")
            except ValueError:
                print("Invalid password")

    def get_private_key(self) -> Optional[rsa.RSAPrivateKey]:
        return self.__private_key

    def reset_private_key(self) -> None:
        self.__private_key = None
