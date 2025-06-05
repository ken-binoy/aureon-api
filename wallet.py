import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)
from cryptography.hazmat.primitives import serialization


def generate_wallet():
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    address = "0x" + hashlib.sha256(public_bytes).hexdigest()[:40]

    return {
        "address": address,
        "public_key": base64.b64encode(public_bytes).decode(),
        "private_key": base64.b64encode(private_bytes).decode()
    }


def import_wallet_from_private_key(b64_private: str):
    private_bytes = base64.b64decode(b64_private)
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    public_key = private_key.public_key()

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    address = "0x" + hashlib.sha256(public_bytes).hexdigest()[:40]

    return {
        "address": address,
        "public_key": base64.b64encode(public_bytes).decode(),
        "private_key": b64_private
    }


def verify_signature(pub_key_b64: str, sig_b64: str, message: str, return_address=False):
    try:
        pub_bytes = base64.b64decode(pub_key_b64)
        public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)

        if return_address:
            address = "0x" + hashlib.sha256(pub_bytes).hexdigest()[:40]
            return address

        signature = base64.b64decode(sig_b64)
        public_key.verify(signature, message.encode())
        return True
    except Exception:
        return False