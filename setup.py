from setuptools import setup

setup(
    name="txssmi",
    version="0.3.0",
    url='http://github.com/smn/txssmi',
    license='BSD',
    description="Twisted library for Truteq's SSMI protocol",
    long_description=open('README.rst', 'r').read(),
    author='Simon de Haan',
    author_email='simon@praekeltfoundation.org',
    packages=[
        "txssmi",
    ],
    package_data={},
    include_package_data=True,
    install_requires=[
        'Twisted',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Framework :: Twisted',
    ],
)
