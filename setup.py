from setuptools import setup, find_packages

setup(
    name='shopping_cart',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'PyQt5~=5.15.9',
    ],
    extras_require={
        'test': ['pytest==7.4.0']
    },
    entry_points={
        'console_scripts': [
            'shopping_cart=shopping_cart.cli:main',
        ],
    },
    package_data={
        'shopping_cart': ['data/*', 'logs/*'],
    }
)
