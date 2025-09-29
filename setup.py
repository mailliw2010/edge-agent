#!/usr/bin/env python3
"""Setup script for Edge Agent"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="edge-agent",
    version="0.1.0",
    author="Edge Agent Team",
    author_email="support@edge-agent.com",
    description="Intelligent AI Agent for edge device management using LangChain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mailliw2010/edge-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Home Automation",
        "Topic :: Internet of Things",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "edge-agent=edge_agent.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "edge_agent": ["config/*.yaml", "config/*.yml"],
    },
    keywords="ai, langchain, iot, edge-computing, air-conditioner, smart-home, automation",
    project_urls={
        "Bug Reports": "https://github.com/mailliw2010/edge-agent/issues",
        "Source": "https://github.com/mailliw2010/edge-agent",
        "Documentation": "https://github.com/mailliw2010/edge-agent/blob/main/README.md",
    },
)