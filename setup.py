from setuptools import setup

setup(
    name='Chromoy',  # This is the name of your PyPI-package.
    author="Alexey Savchenko",
    author_email="beastrock@mail.ru",
    url="https://github.com/Beastrock/Chromoy",
    description="Refreshed chrome-driver for parsing and cron-testing.",
    version='0.05',  # Update the version number for new releases,
    packages=['chromoy'],
    install_requires=[
        'selenium==3.14.0',
        'beautifulsoup4==4.6.3',
        'lxml==4.2.4',
        'PyVirtualDisplay==0.2.1',
        'requests==2.19.1',
        'psutil==5.4.7',
    ],
)
