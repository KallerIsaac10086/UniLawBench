from setuptools import setup, find_packages

setup(
    name='unilawbench',
    version='1.2.post1',
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
        'evalscope[all]'
    ],
    entry_points={
        'console_scripts': [
            'unilawbench=unilawbench.cli:main'
        ]
    }
)