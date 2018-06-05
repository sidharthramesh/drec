import os
from medblocks import EncryptionLayer
from bigchaindb_driver.crypto import generate_keypair, CryptoKeypair
import json

class User(object):
    def __init__(self, name=None, phone=None, rsa=None, bigchain=None, json=None, *args, **kwargs):
        if json is None:
            self.name = name
            self.phone = phone
            if rsa is not None:
                self.rsa = rsa
            else:
                self.rsa = self.generate_rsa()
                print("[o] Creating User object. Generating RSA...")
            
            if bigchain is not None:
                self.bigchain = bigchain
            else:
                self.bigchain = self.generate_bigchain()
                print("[o] Creating User object. Generating BigChain Keypair...")
        else:
            self.json = json
            self = self.from_json()
    def generate_rsa(self):
        return EncryptionLayer.generate_random_RSA()

    def generate_bigchain(self):
        return generate_keypair()

    def to_json(self):
        d = {
            'name':self.name,
            'phone':self.phone,
            'rsa':{
                'public': self.rsa.publickey().exportKey().decode('utf-8'),
                'private': self.rsa.exportKey().decode('utf-8')
            },
            'bigchain':{
                'public': self.bigchain.public_key,
                'private': self.bigchain.private_key
            }
        }
        # with open('test.json','w') as f:
            # f.write(json.dumps(d))
        return json.dumps(d)

    def from_json(self):
        self.json = json.loads(self.json)
        self.name = self.json['name']
        self.phone = self.json['phone']
        self.rsa = EncryptionLayer.RSA.importKey(self.json['rsa']['private'])
        self.bigchain = CryptoKeypair(self.json['bigchain']['private'], self.json['bigchain']['public'])
        del self.json
        return self
