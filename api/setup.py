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
    python_requires=">=3.9, <4",
    install_requires=["uvicorn", "fastapi", "aiosqlite"],  # Optional
    # package_data={  # Optional
    #     "sample": ["package_data.dat"],
    # },
    # Entry points.
    entry_points={  # Optional
        "console_scripts": [
            "envsens-api=envsens:main",
        ],
    },
)
