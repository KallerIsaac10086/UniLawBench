from setuptools import setup, find_packages
import os
import sys

# 读取README文件
def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

setup(
    name='unilawbench',
    version='1.5.1',
    description='中文法律大模型评测工具',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='UniLawBench Team',
    author_email='contact@unilawbench.org',
    url='https://github.com/unilawbench/unilawbench',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    package_data={
        'unilawbench': [
            'dataset/mcq/*.csv',
            'dataset/qa/*.jsonl',
            'dataset/mcq/*',
            'dataset/qa/*',
            'utils/*.py',
            'gui/*.py'
        ]
    },
    install_requires=[
        'PyQt5',
        'pytrec_eval_terrier'
    ],
    extras_require={},
    entry_points={
        'console_scripts': [
            'unilawbench=unilawbench.cli:main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',
)