from setuptools import setup

setup(
    name='P2P',
    version='0.0-dev',
    packages=['p2p', 'p2p.proto', 'p2p.server', 'p2p.utils', 'p2p.client'],
    package_data={'p2p': ['rfcs/*.txt']},
    include_package_data=True,
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
