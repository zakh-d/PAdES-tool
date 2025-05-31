import os

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes

SIGNATURE_SIZE_IN_BYTES = 512


class PDFVerifier:
    """
    Verifies the signature of a PDF file using a public key.
    """

    def __init__(self, public_key: rsa.RSAPublicKey):
        self._public_key = public_key

    def verify(self, pdf_file_path: str) -> bool:
        """
        Verifies the signature of a PDF file.
        :param pdf_file_path: The path to the PDF file.
        :return: True if the signature is valid, False otherwise.
        """
        size_in_bytes = os.path.getsize(pdf_file_path)
        with open(pdf_file_path, "rb") as f:
            pdf_content = f.read(size_in_bytes - SIGNATURE_SIZE_IN_BYTES)
            signature = f.read()

        try:
            self._public_key.verify(
                signature,
                pdf_content,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except InvalidSignature:
            return False
