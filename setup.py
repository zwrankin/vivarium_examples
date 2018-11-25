import os

from setuptools import setup, find_packages


if __name__ == "__main__":

    setup(
        name='vivarium_examples',
        version='1.0',
        description="Examples of simulations built with vivarium",
        author='Zane Rankin',

        package_dir={'': 'src'},
        packages=find_packages(where='src'),
        include_package_data=True,

        install_requires=['vivarium', 'matplotlib', 'imageio', 'sklearn'],
)
