from setuptools import setup

def get_data_files():
    """Get the data files for the package.
    """
    data_files = [
        ('etc/jupyter/jupyter_server_config.d', ['etc/jupyter/jupyter_server_config.d/jupytexpr.json']),
        ('etc/jupyter/jupyter_notebook_config.d', ['etc/jupyter/jupyter_notebook_config.d/jupytexpr.json'])
    ]
    return data_files

requirements = [
    'jupyter_server',
    'nest_asyncio',
    'aiohttp',
    'numpy',
    'bqplot'
]

setup(
    name="jupytexpr",
    version="0.0.1",
    author="David Brochart",
    author_email="david.brochart@gmail.com",
    description="Array expression evaluator for Jupyter",
    long_description="An architecture to process array computing in a Jupyter environment.",
    long_description_content_type="text/markdown",
    url="https://github.com/davidbrochart/jupytexpr",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=requirements,
    data_files=get_data_files()
)
