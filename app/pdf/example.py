from cryptography.hazmat.primitives.asymmetric import rsa

from pdf_signer import PDFSigner
from pdf_verifier import PDFVerifier

priv_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
)

pub_key = priv_key.public_key()

signer = PDFSigner(priv_key)
verifier = PDFVerifier(pub_key)

file_path = "app/pdf/example.pdf"

print("Signing file...")
signer.sign(file_path)
print("File signed")

if verifier.verify(file_path):
    print("Signature is valid")
else:
    print("Signature is invalid")
