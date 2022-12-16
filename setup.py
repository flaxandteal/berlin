#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('requirements.txt') as reqs:
    required = reqs.read().splitlines()

    setup(
        name="berlin",
        version="0.2.2",
        description="Tool to help analyse location statistics",
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                'yourscript = yourscript:cli',
            ],
        },
        setup_requires=['pytest-runner'],
        tests_require=['pytest'],
        install_requires=required
    )
