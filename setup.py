from setuptools import setup, find_packages

setup(
    name='unilawbench',
    version='1.5.0',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
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
        'PyQt5',
        'pytrec_eval_terrier'
    ],
    entry_points={
        'console_scripts': [
            'unilawbench=unilawbench.cli:main'
        ]
    }
)