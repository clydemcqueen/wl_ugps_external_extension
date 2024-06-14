#!/usr/bin/env python3

import os
import ssl

from setuptools import setup

# Ignore ssl if it fails
if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(ssl, "_create_unverified_context", None):
    ssl._create_default_https_context = ssl._create_unverified_context

setup(
    name="wl_ugps_external_extension",
    version="1.0.3",
    description="WL UGPS External Extension",
    license="MIT",
    install_requires=[
        "aiofiles==0.8.0",
        "fastapi==0.109.1",
        "loguru==0.6.0",
        "pynmea2==1.19.0",
        "requests==2.31.0",
        "uvicorn==0.13.4",
    ],
)
