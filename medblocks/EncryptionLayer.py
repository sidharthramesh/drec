from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
import base64
import os

def encrypt_rsa(data, public_key):
    handler = PKCS1_OAEP.new(public_key)
    return base64.encodebytes(handler.encrypt(data))

def decrypt_rsa(data, private_key):
    handler = PKCS1_OAEP.new(private_key)
    return handler.decrypt(base64.decodebytes(data))

def pad(s):
    return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

def encrypt(message, key, key_size=256):
    message = pad(message)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(message)

def decrypt(ciphertext, key):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    return plaintext.rstrip(b"\0")

def encrypt_file(file_name, key):
    with open(file_name, 'rb') as fo:
        plaintext = fo.read()
    enc = encrypt(plaintext, key)
    return enc


def decrypt_file(file_name, key):
    with open(file_name, 'rb') as fo:
        ciphertext = fo.read()
    dec = decrypt(ciphertext, key)
    with open(file_name[:-4], 'wb') as fo:
        fo.write(dec)

def generate_random_aes_key():
    return os.urandom(32)

def generate_random_RSA():
    return RSA.generate(1024, os.urandom)