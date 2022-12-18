# -*- coding: utf-8 -*-

"""

"""

from distutils.core import setup

setup(
        name='Python Essentials',
        version='0.1',
        description='Python utilities I\'ve written and use',
        author='Kami Kaze',
        # todo: author_email='',
        url='https://github.com/Kaze-Kami/klib',
        package_dir={'': 'src'},
        packages=[
            'essentials',
        ],
        license='MIT Licence',
        long_description=open('README.md').read(),
        reqires=open('requirements.txt').readlines(),
)
