# black-isort-flake8-envconfig


## Project

Configuring the development environment to use the libs:
- black
- isort
- flake8


## Libs

**black**
- lib focusing on code formatting in Python;

**isort**
- isort is a Python utility / library to sort imports alphabetically and automatically separate into sections and by type

**flake8**
- is a Python library and command-line tool for enforcing style and improving code quality. It combines multiple tools into a single framework;
- checks if my code complies with PEP 8;


## Step by step to configure the development environment:

**1. Repository creation**
- git clone of the created repo

**2. Copy and paste a .py file**
- create main.py file (or other name);
- to check the libs, copy and paste a .py file from another repo to perform the check;
- the older the better, as the greater the chances of being outside of good practices;

**3. Configure pyenv locally**
```bash
pyenv local 3.12.1
poetry init
poetry env use 3.12.1
poery shell
```

**3.1. Install flake8 lib**
```bash
poetry add flake8
poetry run flake8
```
- return examples:
    - F401 'pyspark.sql.SparkSession' imported but unused
    - E302 expected 2 blank lines, found 1
    - W293 blank line contains whitespace