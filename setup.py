from setuptools import setup

setup(
    name="r3d-hunt3r",
    version="1.0.0",
    py_modules=["cyberowl"],
    install_requires=["rich", "click"],
    entry_points={
        "console_scripts": [
            "r3d-hunt3r=cyberowl:cli",
        ],
    },
    python_requires=">=3.8",
)
