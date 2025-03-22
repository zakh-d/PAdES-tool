import os

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes

SIGNATURE_SIZE_IN_BYTES = 512


class PDFVerifier:
    def __init__(self, public_key: rsa.RSAPublicKey):
        self._public_key = public_key

    def verify(self, pdf_path: str) -> bool:
        size_in_bytes = os.path.getsize(pdf_path)
        with open(pdf_path, "rb") as f:
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
