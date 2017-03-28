#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pickle
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)

class Crypto:
    def __init__(self, key_path="public.pem", flag=0):
        with open(key_path, 'rb') as key_file:
            if flag == 0: # Client
                self.public_key = serialization.load_pem_public_key(
                        key_file.read(),
                        backend=default_backend()
                    )
                self.private_key = None
            else: # Server
                self.public_key = None
                self.private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )
        
    def rsa_encrypt(self, plaintext):
        assert self.public_key is not None

        ciphertext = self.public_key.encrypt(
                plaintext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )
        return ciphertext

    def rsa_decrypt(self, ciphertext):
        assert self.private_key is not None

        plaintext = self.private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                )
            )
        return plaintext

    def symmetric_init(self):
        self.key = os.urandom(16)

    def symmetric_encrypt(key, plaintext, associated_data):
        # Generate a random 96-bit IV.
        iv = os.urandom(12)

        # Construct an AES-GCM Cipher object with the given key and a
        # randomly generated IV.
        encryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            ).encryptor()

        # associated_data will be authenticated but not encrypted,
        # it must also be passed in on decryption.
        encryptor.authenticate_additional_data(associated_data)

        # Encrypt the plaintext and get the associated ciphertext.
        # GCM does not require padding.
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return (iv, ciphertext, encryptor.tag)

    def symmetric_decrypt(key, associated_data, iv, ciphertext, tag):
        # Construct a Cipher object, with the key, iv, and additionally the
        # GCM tag used for authenticating the message.
        decryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            ).decryptor()

        # We put associated_data back in or the tag will fail to verify
        # when we finalize the decryptor.
        decryptor.authenticate_additional_data(associated_data)

        # Decryption gets us the authenticated plaintext.
        # If the tag does not match an InvalidTag exception will be raised.
        return decryptor.update(ciphertext) + decryptor.finalize()

en = Crypto()
de = Crypto("private.pem", 1)
e = en.rsa_encrypt(b"Hello")
print(de.rsa_decrypt(e))
