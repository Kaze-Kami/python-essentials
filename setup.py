# -*- coding: utf-8 -*-

"""

"""

from distutils.core import setup

setup(
        name='Python Essentials',
        version='0.1.dev2',
        description='Python utilities I\'ve written and use',
        author='Kami Kaze',
        # todo: author_email='',
        url='https://github.com/Kaze-Kami/python-essentials',
        package_dir={'': 'src'},
        packages=[
            'essentials',
            'essentials.containers',
            'essentials.gui',
            'essentials.io',
            'essentials.itertools',
            'essentials.mt_processor',
            'essentials.tui',
            'essentials.util',
        ],
        license='MIT Licence',
        long_description=open('README.md').read(),
        install_requires=open('requirements.txt').read().split('\n'),
)
