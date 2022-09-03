from distutils.core import setup
import setuptools

setup(
    name='pyODM',
    version='0.1dev',
    packages=setuptools.find_packages(),
    license='MIT License',
    long_description=open('README.md').read(),
    install_requires=['datetime', 'numpy', 'pandas', 'scipy']
)
