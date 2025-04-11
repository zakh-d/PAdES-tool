from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from .singleton_meta import SingletonMeta


class PublicKey(metaclass=SingletonMeta):
    """
    A class for managing the public key.
    Only one instance of the class can exist throughout the application.
    """

    def __init__(self):
        self.__public_key = None

    def load_public_key(self, public_key_path: str) -> None:
        """
        Loads the chosen public key from the specified path.
        :param:
            public_key_path: The path to the public key file.
        """
        with open(public_key_path, "rb") as f:
            try:
                self.__public_key = serialization.load_pem_public_key(f.read())
                print("Public key was loaded")
            except ValueError:
                print("Wrong file")

    def get_public_key(self) -> Optional[rsa.RSAPublicKey]:
        return self.__public_key
