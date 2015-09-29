from setuptools import setup, find_packages

requires = [
    'pycurl==7.19.5.1',
    'tornado==4.2.1'
]

test_requires = [
]


setup(
    name='tormon',
    install_requires=requires,
    tests_require=test_requires,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    version='0.0.11',
    description=(
        'Tornado based application monitor'
    ),
    author='jnosal',
    author_email='jacek.nosal@outlook.com',
    url='https://github.com/jnosal/tormon',
    keywords=[
        'tornado', 'redis', 'tormon'
    ],
    entry_points={
        'console_scripts': [
            'tor-mon = tormon.run:main',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
