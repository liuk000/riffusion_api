from setuptools import setup, find_packages

setup(
    name='discord_tools',
    version='0.1019',
    packages=find_packages(),
    install_requires=[
        'requests~=2.31.0',
        'pydub~=0.25.1'
    ],
)
