import click
from click import echo, secho
import os
import json
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair, CryptoKeypair
import requests
import ipfsapi
import time
from encryption import *
bdb = BigchainDB(
    'https://test.bigchaindb.com',
    headers={'app_id': 'd5596f54',
             'app_key': '6f108c571fcb25c4d34056bede9d246f'})
credentials_path = os.path.expanduser('~/.medblocks')
version = '0.01'
emergency_address = '3gk3RzXuchFZrHuPjQQb6Aeyevs16t6e2GnSh7qkTUJ1'

@click.group()
@click.version_option(version, message=version)
def main():
    """
    \b
    ███╗   ███╗███████╗██████╗ ██████╗ ██╗      ██████╗  ██████╗██╗  ██╗███████╗
    ████╗ ████║██╔════╝██╔══██╗██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝██╔════╝
    ██╔████╔██║█████╗  ██║  ██║██████╔╝██║     ██║   ██║██║     █████╔╝ ███████╗
    ██║╚██╔╝██║██╔══╝  ██║  ██║██╔══██╗██║     ██║   ██║██║     ██╔═██╗ ╚════██║
    ██║ ╚═╝ ██║███████╗██████╔╝██████╔╝███████╗╚██████╔╝╚██████╗██║  ██╗███████║
    ╚═╝     ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝ 
    Store your medical records securely                                         
    """
    
def dump_user(user):
    """Converts user dictionary to json string"""
    bigchain_keys = user['bigchain']
    user['bigchain'] = {'private_key':bigchain_keys.private_key, 'public_key':bigchain_keys.public_key}
    # Serialize rsa 
    rsa_key = user['rsa']
    user['rsa'] = {'private_key':rsa_key.exportKey().decode('utf-8'),'public_key':rsa_key.publickey().exportKey().decode('utf-8')}
    echo("[+] Serializing to JSON")
    user = json.dumps(user)
    return user

def load_user(string):
    """Loads json string into user dictionary"""
    user = json.loads(string)
    user['rsa'] = RSA.importKey(user['rsa']['private_key'])
    user['bigchain'] = CryptoKeypair(user['bigchain']['private_key'],user['bigchain']['public_key'])
    return user

def load(file=credentials_path):
    """Loads user dictionary from credentials_path"""
    try:
        with open(file, 'r') as f:
            user = load_user(f.read())
    except FileNotFoundError:
        echo("[-] No user logged in. Please login.")
        click.secho("Hint: Use 'createuser' to create a user json file", fg='green')
        return None
    return user

def register_on_blockchain(string):
    user_dict = json.loads(string)
    data = {
        'schema':'medblocks.user',
        'version':'v0.01',
        'rsa':user_dict['rsa']['public_key'],
        'bigchain':user_dict['bigchain']['public_key'],
        'phone':user_dict['phone'],
        'name':user_dict['name']
    }
    echo("[+] Preparing CREATE transaction with {}...".format(str(data)[:10]))
    tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=user_dict['bigchain']['public_key'],
    asset={'data': data})

    echo("[+] Signing with private key")
    signed_tx = bdb.transactions.fulfill(
    tx,
    private_keys=user_dict['bigchain']['private_key']
    )
    echo("[+] Sending to the Blockchain")
    sent = bdb.transactions.send(signed_tx)
    echo("[+] Sent transaction {}".format(sent))
    return sent
    # mobile => address, rsa_key
    # address => [{ ipfs hash, cipher, emergency_cipher}]

current_user = load()


def filter(l, key, value):
    new_list = []
    for instance in l:
        data = instance.get('data')
        if data.get(key) == value:
            new_list.append(instance)
    return new_list

def version_filter(l):
    return filter(l, 'version','v'+version)
    
    
class Patient(object):
    def __init__(self, mobile=None, public_key=None):
        self.registered = None
        self.records = None
        if mobile is not None:
            self.bio = self.get_bio_from_mobile(mobile)
        if public_key is not None:
            self.bio = self.get_bio_from_public_key(public_key)
        self.medblocks = []
        self.non_keyed = []
        self.get_medblocks()
        
    def get_bio_from_mobile(self, mobile):
        records = bdb.assets.get(search=mobile)
        records = filter(records, 'schema','medblocks.user')
        if len(records) == 1:
            echo("[+] Found user with mobile number!")
            self.registered = True
            return records[0]['data']
        if len(records) > 1:
            secho("[o] Got more than one record for the same version. Last registery will be taken",fg='yellow')
            self.registered = True
            return records[-1]['data']
        
        secho("[-] No user with that phone number registered", fg='red')
        self.registered = False
        return

    def get_bio_from_public_key(self, public_key):
        self.records = bdb.assets.get(search=public_key)
        registers = filter(self.records, 'schema','medblocks.user')

        if len(registers) == 1:
            self.registered = True
            return registers[0].get('data')

        if len(registers) > 1:
            secho("[o] Got more than one record for the same version. Last registery will be taken",fg='yellow')
            self.registered = True
            return registers[-1].get('data')
        
        secho("[-] No user with that public key registered", fg='red')
        self.registered = False
        return

    def get_medblocks(self):
        """Gets all medblocks where 'patient' address is current patient's"""
        if self.records is None:
            self.records = bdb.assets.get(search=self.bio['bigchain'])
    
        for record in self.records:
            if record.get('data').get('schema') == 'medblocks.medblock' and record.get('data')['patient'] == self.bio['bigchain']:
                self.medblocks.append(record)

        self.medblocks = version_filter(self.medblocks)
        keyed_blocks = []
        non_keyed = []
        for medblock in self.medblocks:
            asset_id = medblock['id']
            keys = self.get_keys(asset_id)
            medblock['owned'] = self.owner_is_patient(asset_id)
            if len(keys) > 0:
                medblock['keys']=keys
                keyed_blocks.append(medblock)
            else:
                non_keyed.append(medblock)
        
        self.medblocks = keyed_blocks
        self.non_keyed = non_keyed
        
    def has_permission(self, medblock):
        if current_user['bigchain'].public_key in medblock['keys'].keys():
            return medblock['keys'][current_user['bigchain'].public_key]
        return False
    
    def get_owner(self, asset_id):
        txns = bdb.transactions.get(asset_id=asset_id)
        return txns[-1]['outputs'][0]['condition']['details']['public_key']
    
    def owner_is_patient(self, asset_id):
        owner = self.get_owner(asset_id)
        if owner == self.bio['bigchain']:
            return True
        else:
            return False
    
    def get_keys(self, asset_id):
        keys = {}
        txns = bdb.transactions.get(asset_id=asset_id)
        for tx in txns:
            meta = tx.get('metadata')
            if meta is not None:
                for k in meta['keys']:
                    keys[k] = meta['keys'][k]
        return keys
    
    def display_medblocks(self):
        for i, medblock in enumerate(self.medblocks):
            echo("------------------------------------Medblock {}------------------------------------".format(i+1))
            secho("ID: {}".format(medblock['id']), fg='yellow')
            echo("IPFS hash: {}".format(medblock['data']['ipfs_hash']))
            echo("File Format: {}".format(medblock['data']['type']))
            keys = self.get_keys(medblock['id'])
            if emergency_address in keys.keys():
                secho("**EMERGENCY BLOCK**", fg='red')
            echo("Permitted addresses: {}".format(len(keys)))
            if self.has_permission(medblock):
                secho("Current user can decrypt", fg='green')
            else:
                secho("Current user cannot decrypt", fg='red')
            echo("----------------------------------------------------------------------------------")

    def write_medblock(self, ipfs_hash, encrypted_key, emergency_key=None, format=None):
        data = {
        'schema':'medblocks.medblock',
        'version':'v0.01',
        'type': format,
        'ipfs_hash': ipfs_hash,
        'patient': self.bio['bigchain']
        }
        metadata = {
            'schema':'medblocks.aes', 
            'keys': {
                self.bio['bigchain']: encrypted_key
                }
        }

        if emergency_key is not None:
            metadata['keys'][emergency_address] = emergency_key
        
        echo("[+] Preparing CREATE transaction with {}...".format(str(data)[:10]))
        tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=current_user['bigchain'].public_key,
        asset={'data': data},
        metadata=metadata
        )
        echo("[+] Signing with private key")
        signed_tx = bdb.transactions.fulfill(
        tx,
        private_keys=current_user['bigchain'].private_key
        )
        echo("[+] Creating MedBlock on the Blockchain")
        sent = bdb.transactions.send(signed_tx)
        echo("[+] Created: {}".format(sent['id']))
        self.transfer_medblock(sent)
    
    def transfer_medblock(self, tx, metadata=None):
        echo("[+] Transfering MedBlock to patient: {}".format(self.bio['bigchain']))
        output = tx['outputs'][0]
        transfer_input = {
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output_index': 0,
                'transaction_id': tx['id'],},
            'owners_before': output['public_keys'],}
        if tx['operation'] == 'TRANSFER':
            asset_id = tx['asset']['id']
        else:
            asset_id = tx['id']

        transfer_asset = {
            'id':asset_id,
        }
        echo("[+] Preparing TRANSFER transaction with encrypted key")
        if metadata is None:
            prepared_tx = bdb.transactions.prepare(
                operation='TRANSFER',
                asset=transfer_asset,
                inputs=transfer_input,
                recipients=self.bio['bigchain'],
            )
        else:
            prepared_tx = bdb.transactions.prepare(
                operation='TRANSFER',
                asset=transfer_asset,
                inputs=transfer_input,
                recipients=self.bio['bigchain'],
                metadata=metadata
            )
        echo("[+] Signing transaction")
        signed = bdb.transactions.fulfill(
            prepared_tx,
            private_keys=current_user['bigchain'].private_key
        )
        for attempt in range(10):
            block = bdb.blocks.get(txid=tx['id'])
            if block is not None:
                echo("[+] Asset block confirmed on the blockchain: {}".format(block))
                break
            echo("[o] Waiting for the asset block to confirm on blockchain. Sleeping for 0.5...")
            time.sleep(0.5)
        echo("[+] Sending on the blockchain")
        tx = bdb.transactions.send(signed)
        secho("[+] Transaction sent: {}".format(tx['id'], fg='green'))


def ipfs_connect():
    try:
        api = ipfsapi.connect('127.0.0.1', 5001)
        secho("[+] Connected to local IPFS node", fg='green')
    except ipfsapi.exceptions.ConnectionError:
        secho("[-] Local IPFS daemon not running. Exiting...", fg='red')
        exit(1)
    return api

def give_permission(address, medblock_index):
    pass

@main.command()
@click.option('--output','-o', help="Output file with credentials", default='user.json')
@click.option('--name','-n',prompt="Name of patient")
@click.option('--phone','-p',prompt="Phone number")
def createuser(name, phone, output):
    """Generate a user file data"""
    user = {
        'name':name,
        'phone':phone
    }
    echo("[+] Writing Name and Phone")
    echo("[+] Generating BigChainDB keypair")
    bigchain_keys = generate_keypair()
    user['bigchain'] = bigchain_keys
    random_generator = Random.new().read
    rsa_key = RSA.generate(1024, random_generator)
    echo("[+] Generating RSA keypair")
    user['rsa'] = rsa_key
    st = dump_user(user)
    click.secho("Writing private key data to a json file. Please be sure to save it securely. You will need it to log in later.", fg='yellow')
    click.pause()
    echo("[+] Writing file to disk as: {}".format(output))
    with open(output,'w') as f:
        f.write(st)

@main.command()
def register():
    """Register current user on the blockchain"""
    user = load()
    register_on_blockchain(dump_user(user))

@main.command()
@click.argument('login', type=click.Path(exists=True))
@click.pass_context
def login(ctx, login):
    """Log in with a user file"""
    user = load(login)
    if click.confirm(text="This will overwrite all previous user data. Are you sure?"):
        echo("[+] Writing to .medblocks")
        with open(credentials_path,'w') as f:
            f.write(dump_user(user))
    ctx.invoke(info)

@main.command()
def info():
    """Get info about current user"""
    echo("[+] Loading user from .medblocks")
    user = load()
    echo('Name: {}'.format(user['name']))
    echo('Phone: {}'.format(user['phone']))
    echo('RSA public key: ')
    secho(user['rsa'].publickey().exportKey().decode(), fg='green')
    echo('Bigchain public key: {}'.format(user['bigchain'].public_key))
    # Check registered on BigChainDB
    
    echo("[+] Loading all records of user on the blockchain")
    publicpatient = Patient(public_key=user['bigchain'].public_key)
    if publicpatient.registered:
        secho('Registered on the Blockchain!', fg='green')
    else:
        secho("Not yet registered on the Blockchain. Register with the 'register' command",fg='yellow')
    echo("MedBlocks: {}".format(len(publicpatient.medblocks)))

def get_patient(address, phone):
    if address is None and phone is None:
        echo("[o] No address or phone number provided. Loading current logged in user")
        user = load()
        publicpatient = Patient(public_key=user['bigchain'].public_key)
    if address is not None:
        publicpatient = Patient(public_key=address)
    if phone is not None:
        publicpatient = Patient(mobile=phone)
    return publicpatient

@main.command()
@click.option('--address', '-a', help="The bigchain address of the patient")
@click.option('--phone','-p',help="The phone numer of the patient")
def list(address, phone):
    """List all medblocks of current user"""
    publicpatient = get_patient(address, phone)
    publicpatient.display_medblocks()

@main.command()
@click.option('--phone','-t', help="Mobile number of the patient")
@click.option('--address','-a', help="Public key of the patient")
@click.option('--emergency','-e', help="IS EMERGENCY DATA", is_flag=True)
@click.argument('file',type=click.Path(exists=True))
def add(file, phone, address, emergency):
    """Create a medblock with a file"""
    echo("[+] Fetching user data from the blockchain")
    patient = get_patient(address, phone)
    public_rsa = patient.bio['rsa']
    echo("[+] Got Public RSA key")
    secho(public_rsa, fg='green')
    public_rsa = RSA.importKey(public_rsa)
    echo("[+] Generating random AES key")
    key = generate_random_aes_key()
    echo("[+] Encrypting data...")
    enc = encrypt_file(file, key)
    secho("[+] Writing encrypted data to IPFS", fg='yellow')
    api = ipfs_connect()
    ipfs_hash = api.add_bytes(enc)
    secho("[+] Data written to IPFS: {}".format(ipfs_hash), fg='green')
    echo("[+] Encrypting AES key with RSA public key")
    encrypted_key = encrypt_rsa(key, public_rsa)
    encrypted_key = encrypted_key.decode()

    # Create MedBlock
    if len(file.split('.'))> 0:
        format = file.split('.')[-1]
    
    if emergency:
        emergency_account = Patient(public_key=emergency_address)
        emergency_rsa = RSA.importKey(emergency_account.bio['rsa'])
        emergency_key = encrypt_rsa(key, emergency_rsa)
        emergency_key = emergency_key.decode()
        patient.write_medblock(ipfs_hash, encrypted_key, emergency_key, format=format)
    else:
        patient.write_medblock(ipfs_hash, encrypted_key, format=format)

@main.command()
@click.option('--address', '-a', help="The bigchain address of the patient")
@click.option('--phone','-p',help="The phone numer of the patient")
@click.option('--all', is_flag=True)
@click.argument('asset')
def permit(asset, address, phone, all):
        """Permit someone to decrypt a medblock"""
        doctor = get_patient(address, phone)
        recorded_keys = doctor.get_keys(asset)
        if doctor.bio['bigchain'] in recorded_keys:
            echo("[+] Permission already granted")
            exit()
        
        user_patient = Patient(public_key=current_user['bigchain'].public_key)
        if user_patient.owner_is_patient(asset):
            tx = bdb.transactions.get(asset_id=asset)[-1]
            public_rsa = doctor.bio['rsa']
            echo("[+] Got Public RSA key")
            secho(public_rsa, fg='green')
            public_rsa = RSA.importKey(public_rsa)
            
            encrypted_key = recorded_keys[user_patient.bio['bigchain']]
            # Decrypt key
            echo("[+] Decrypting AES key using private key")
            decrypted_key = decrypt_rsa(encrypted_key.encode(), current_user['rsa'])
            echo("[+] Decrypted : {}".format(decrypted_key))
            click.pause()
            echo("[+] Encrypting AES key with RSA public key")
            encrypted_key = encrypt_rsa(decrypted_key, public_rsa)
            encrypted_key = encrypted_key.decode()
            user_patient.transfer_medblock(tx,metadata={
                                            'schema':'medblocks.aes', 
                                            'keys': {
                                                doctor.bio['bigchain']: encrypted_key
                                                }
                                        })
        else:
            echo("[-] Current user not owner of medblock. Please login with a different account")
@main.command()
@click.argument('asset')
@click.option('--output','-o',type=click.Path(), help='Output path for file')
def get(asset, output):
    """Retrive and decrypt medblock"""
    user_patient = Patient(public_key=current_user['bigchain'].public_key)
    keys = user_patient.get_keys(asset)
    if current_user['bigchain'].public_key in keys.keys():
        secho("[+] Current user has permission to decrypt", fg='green')
        data = bdb.transactions.get(asset_id=asset)[0]['asset']['data']
        
        
        echo("[+] Decrypting AES key")
        encrypted_key = keys[current_user['bigchain'].public_key]
        encrypted_key = encrypted_key.encode()
        key = decrypt_rsa(encrypted_key, current_user['rsa'])
        echo("[+] Retrtriving file from IPFS")
        api = ipfs_connect()
        encrypted = api.cat(data['ipfs_hash'])
        echo("[+] Decrypting file")
        decrypted = decrypt(encrypted, key)
        secho("[+] File decrypted", fg='green')
        echo("Length: {}".format(len(decrypted)))
        echo("...Head display...", nl=True)
        echo(decrypted[:600], nl=True)
        echo("",nl=True)
        if output is None:
            output = '.'.join([asset, data['type']])
        echo("[+] Writing to {}".format(output))
        with open(output, 'wb') as f:
            f.write(decrypted)
        secho("[+] Done!", fg='green')
    else:
        secho("[+] Current user does has permission to decrypt", fg='red') 
        exit(1)
if __name__ == "__main__":
    main()