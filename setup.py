from setuptools import setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='FlowIO',
    version='0.9.12',
    packages=['flowio'],
    package_data={'': []},
    description='FlowIO is a Python library for reading / writing Flow Cytometry Standard (FCS) files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Scott White',
    author_email='whitews@gmail.com',
    license='BSD',
    url='https://github.com/whitews/flowio',
    requires=[],
    data_files=[('', ['LICENSE'])],
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6'
    ]
)
