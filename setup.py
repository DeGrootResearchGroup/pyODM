from distutils.core import setup

setup(
    name='pyODM',
    version='0.1dev',
    packages=['pyodm',],
    license='MIT License',
    long_description=open('README.md').read(),
    install_requires=['datetime', 'numpy', 'pandas', 'scipy', 'warnings']
)
