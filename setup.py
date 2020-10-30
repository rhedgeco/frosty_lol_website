from setuptools import setup

setup(
    name='frosty_lol_website',
    version='1.0.0',
    install_requires=[
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "cachecontrol",
        'google',
        'requests',
        'sanic',
        'websockets'
    ]
)
