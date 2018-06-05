from setuptools import setup

setup(
    name='medblocks',
    version='0.01',
    py_modules=['medblocks'],
    install_requires=[
        'bigchaindb-driver==0.5.0a4',
        'click==6.7',
        'cryptoconditions==0.6.0.dev1',
        'pycrypto==2.6.1',
        'ipfsapi'],
    entry_points='''
        [console_scripts]
        medblocks=medblocks:main
    ''',
)
