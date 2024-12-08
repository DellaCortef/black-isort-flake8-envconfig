# black-isort-flake8-envconfig


## Project

Configuring the development environment to use the libs:
- black
- isort
- flake8


## Libs

**black**
- lib focusing on code formatting in Python;
- unlike flake8 which only suggests changes, lib black makes the changes;

**isort**
- isort is a Python utility / library to sort imports alphabetically and automatically separate into sections and by type;
- unlike flake8 which only suggests changes, lib isort makes the changes;

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
poetry shell
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

**3.2. Install black lib**
```bash
poetry add black
poetry run black main.py
```

**3.3. Install isort lib**
```bash
poetry add isort
poetry run black main.py
```

**4. pyproject updating**
- if we run black after isort, it will change what isort did;
the same goes for executing isort after black;
- to do this, we must configure the puproject so that they are aligned;
- adding to the isort that lib black will be responsible for formatting:
```python
[tool.isort]
profile = "black"
```

**5. Adding taskipy**
- we can add the taskipy lib to create a command to execute the 3 libs (flake8, black, isort) at the same time;
```python
[tool.taskipy.tasks]
format = """
isort main.py
black main.py
flake8 main.py
"""
```

**6. Creating flake8 file**
- within the file, we can configure the "discrepancies" between the libs;
```python
[flake8]
max-line-length = 89
extend-ignore   = E302, ....
```

**7. pre-commit**
- configure code reviews to evaluate the commit. If it is within what was established by the team, you can add;
- it is possible to add as many pre-commits as you want to make the project more secure, robust, and with governance;
- we can configure pre-commit with the previous 3 libs;
```bash
poetry add pre-commit
```
- creating .pre-commit-config.yaml file to add the configs:
    - spelling errors
    - hard-coded secrets
    - security analysis tool
    - checking good practices in the use of environment variables
    - libs:
        - black
        - isort
        - flake8
