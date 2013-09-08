try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'IG Anylfest',
    'author': 'Intrepids',
    'url': 'http://intrepidusgroup.com',
    'download_url': '',
    'author_email': 'max@intrepidusgroup.com',
    'version': '0.2',
    'install_requires': [],
    'packages': ['anylfest'],
    'scripts': [],
    'name': 'anylfest'
}

setup(**config)

