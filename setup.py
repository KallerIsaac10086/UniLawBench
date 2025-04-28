from setuptools import setup, find_packages

setup(
    name='unilawbench',
    version='1.4.0',
    packages=find_packages(),
    package_data={
        'unilawbench': [
            'dataset/mcq/*.csv',
            'dataset/qa/*.jsonl',
            'dataset/mcq/*',
            'dataset/qa/*',
            'utils/*.py'
        ]
    },
    install_requires=[
        'evalscope[all]',
        'PyQt5==5.15.9'
    ],
    entry_points={
        'console_scripts': [
            'unilawbench=unilawbench.cli:main'
        ]
    }
)