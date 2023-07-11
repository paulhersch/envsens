"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="envsens-api",  # Required
    version="0.0.1rc1",  # Required
    packages=['envsens'],
    python_requires=">=3.9, <4",
    install_requires=[
        "uvicorn",
        "fastapi",
        "aiosqlite",
        "aiofiles",
        "scikit-learn",
        "tensorflow",
        "numpy",
        "keras",
    ],
    package_data={
        'envsens': ['*', '*/*', 'webview/static/*']
    },
    # Entry points.
    entry_points={  # Optional
        "console_scripts": [
            "envsens-api=envsens:main",
        ],
    },
)
