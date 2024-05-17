from setuptools import setup, find_packages

setup(
    name='lokicli',
    version='1.1.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'altgraph',
        'certifi',
        'charset-normalizer',
        'idna',
        'packaging',
        'pyinstaller',
        'pyinstaller-hooks-contrib',
        'requests',
        'urllib3',
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'lokicli = lokicli.lokicli:main',
        ]
    },

    author='Satyam Sundaram',
    author_email='satyamsundaram01@gmail.com',
    description='A CLI app for interacting with Loki API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/satyamsundaram/lokicli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
