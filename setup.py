from setuptools import setup, find_packages

setup(
    name='pystoorm',
    version='0.0.1',
    description='Create an easy database layer',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.5',
    install_requires=[
        'clint>=0.5.1',
        'mysql-connector-python>=8.0.33',
        'PyYAML>=6.0',
        'Mako>=1.2.4',
    ],
    author='Harald Stowasser',
    author_email='pystoorm@stowasser.tv',
    keywords=['orm','database'],
    url='https://github.com/StowasserH/pystoorm'
)
