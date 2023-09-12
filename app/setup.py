#!/usr/bin/env python3

import os
import ssl

from setuptools import setup

# Ignore ssl if it fails
if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(ssl, "_create_unverified_context", None):
    ssl._create_default_https_context = ssl._create_unverified_context

setup(
    name="wl_ugps_external_extension",
    version="0.1.0",
    description="WL UGPS External Extension",
    license="MIT",
    install_requires=[
        "aiofiles==0.8.0",
        "fastapi==0.63.0",
        "loguru==0.5.3",
        "pydantic==1.10.12",
        "pynmea2==1.19.0",
        "requests==2.31.0",
        "setuptools==65.5.1",
        "starlette==0.13.6",
        "uvicorn==0.13.4",
    ],
)
