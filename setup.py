from setuptools import setup, find_packages

setup(
    name="okx_bot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'ccxt',
        'requests',
        'python-dotenv',
    ],
)
