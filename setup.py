from distutils.core import setup

setup(
    name='P2P',
    version='0.0-dev',
    packages=['p2p', 'p2p.protocol', 'p2p.rs', 'p2p.utils', 'p2p.client'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
