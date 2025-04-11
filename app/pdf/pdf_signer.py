from typing import Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class PDFSigner:
    """
    Signs a PDF file using a private key. Signature is appended to the end of the file.
    """

    def __init__(self, private_key: rsa.RSAPrivateKey) -> None:
        self._private_key = private_key

    def _generate_signature(self, pdf_file_path: str) -> Optional[bytes]:
        """
        Generates a signature for the PDF file by signing SHA256 hash of the file content.
        :param pdf_file_path: The path to the PDF file.
        """
        try:
            with open(pdf_file_path, "rb") as f:
                pdf_content = f.read()
            signature = self._private_key.sign(
                pdf_content,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return signature
        except FileNotFoundError:
            return None

    def sign(self, pdf_file_path: str) -> None:
        """
        Signs a PDF file with the private key.
        :param pdf_file_path: The path to the PDF file.
        """
        signature = self._generate_signature(pdf_file_path)

        if signature is None:
            return

        with open(pdf_file_path, "ab") as f:
            f.write(signature)
