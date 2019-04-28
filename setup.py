from setuptools import setup

import simple_git_deploy


def readfile(name):
    with open(name) as f:
        return f.read()

README = readfile('README.md')

setup(
    name='simple-git-deploy',
    version=simple_git_deploy.__version__,
    description='A command-line utility for easy and reliable management of manual deployments from Git repositories',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/edudobay/simple-git-deploy',
    license='GPLv3',
    author='Eduardo Dobay',
    author_email='edudobay@gmail.com',
    project_urls={
        'Source': 'https://github.com/edudobay/simple-git-deploy',
        'Issue Tracker': 'https://github.com/edudobay/simple-git-deploy/issues',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Version Control :: Git',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    keywords='deployment automation git',
    python_requires='>=3.5',
    install_requires=[
        'dateparser>=0.7.0',
        'inquirer',
    ],
    packages=['simple_git_deploy'],
    entry_points={
        'console_scripts': [
            'simple-git-deploy = simple_git_deploy.cli:main',
        ],
    },
)
