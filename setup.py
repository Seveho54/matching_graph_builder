from setuptools import setup

setup(
    name='matching_graph_builder',
    version='0.1.0',
    description='A package to build matching graphs',
    author='Mathias Fuchs',
    author_email='fuchsmath@gmail.com',
    packages=['matching_graph_builder'],
    install_requires=['networkx',
                      'numpy',
                      ],

)