import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="Stock Price Demo",
    version="0.9.0",
    author="Darien Hager",
    author_email="project+stockdemo@technofovea.com",
    description="Analyzes data from Quandl Wiki Prices",
    license="MIT License",
    url="http://github.com/DHager/stock_stats_demo",
    packages=['stock_stats'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
    ],
    entry_points={
        'console_scripts': ['stock_stats=stock_stats.command_line:shell_entry'],
    },
    python_requires='>3.6.0',
    install_requires=['dateutil']
)
