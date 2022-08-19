from base64 import b64encode, b64decode
from nacl.public import PrivateKey


def generate_key():
    """ Генерируем приватный ключ """
    private = PrivateKey.generate()
    return b64encode(bytes(private)).decode("ascii")


def public_key(private_key):
    """ Генерируем публичный ключ на основе приватного """
    private = PrivateKey(b64decode(private_key))
    return b64encode(bytes(private.public_key)).decode("ascii")