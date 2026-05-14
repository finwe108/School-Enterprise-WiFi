from setuptools import setup, find_packages

setup(
    name="wifi-manager",
    version="1.0.0",
    description="Cross-platform WiFi manager with CLI and GUI",
    author="WiFi Manager",
    packages=find_packages(),
    install_requires=[
        "Click==8.1.7",
        "PyQt6==6.6.1",
        "pywifi==0.6.1",
        "keyring==24.3.0",
    ],
    entry_points={
        "console_scripts": [
            "wifi-manager=src.main:main",
        ],
    },
    python_requires=">=3.9",
)
