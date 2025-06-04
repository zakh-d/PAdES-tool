from typing import Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from .singleton_meta import SingletonMeta
import logging

logger = logging.getLogger(__name__)


class PublicKey(metaclass=SingletonMeta):
    """
    A class for managing the public key.
    Only one instance of the class can exist throughout the application.
    """

    def __init__(self):
        self.__public_key = None

    def load_public_key(self, public_key_path: str) -> bool:
        """
        Loads the chosen public key from the specified path.
        :param:
            public_key_path: The path to the public key file.
        :return:
            True if the public key was loaded successfully, False otherwise.
        """
        try:
            with open(public_key_path, "rb") as f:
                self.__public_key = serialization.load_pem_public_key(f.read())
                logger.info("Public key was loaded")
                return True
        except FileNotFoundError:
            logger.error("Public key file not found")
            return False
        except ValueError:
            logger.error("Failed to load public key from the file")
            return False

    def reset_public_key(self) -> None:
        self.__public_key = None
        logger.info("Public key was reset")

    @property
    def value(self) -> Optional[rsa.RSAPublicKey]:
        return self.__public_key
