from setuptools import setup, find_packages

setup(
    name="tasks-cli-maker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "psycopg2-binary",
    ],
    entry_points={
        "console_scripts": [
            "tasks-cli-maker=task_cli.cli:main",
        ],
    },
    author="Ali Mohammadnia",
    author_email="alimohammadnia127@gmail.com",
    description="A task management CLI with PostgreSQL and JSON fallback",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PsymoNiko/task-tracker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
