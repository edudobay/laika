from setuptools import setup

setup(
    name='simple-git-deploy',
    version='0.1.0',
    description='Script for managing deployments from Git repositories',
    url='https://github.com/edudobay/simple-git-deploy',
    license='MIT',
    author='Eduardo Dobay',
    author_email='edudobay@gmail.com',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=[
        'inquirer',
    ],
    packages=['simple_git_deploy'],
    entry_points={
        'console_scripts': [
            'simple-git-deploy = simple_git_deploy.cli:main',
        ],
    },
)
