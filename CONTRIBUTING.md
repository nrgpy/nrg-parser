# ![NRGPy](https://www.gravatar.com/avatar/6282094b092c756acc9f7552b164edfe?s=24) nrg_parser

## Issues

Use the Issues section of **nrg_parser** in GitHub for

- Reporting bugs
- Requesting new features or improvements

## Pull Requests

To submit new features or bug fixes

1. Fork this repository
1. Create a new branch with a descriptive name (i.e. dave-c-fixing-console-print-bug)
1. Commit your changes
1. Open a pull request

For a good example of this process, see the [First Contributions](https://github.com/firstcontributions/first-contributions#first-contributions) GitHub repository.

## Local Dev

To setup a local development environment we recommend using python's venv module.

Follow these steps to clone this repo, setup a local dev environment, and checkout
a new branch to edit

### Windows

```powershell
git clone https://github.com/nrgpy/nrg-parser
cd nrg-parser
python -m venv venv
.\venv\Scripts\activate
pip install -e .[dev,test]
```

### Linux/Mac

```bash
git clone https://github.com/nrgpy/nrg-parser
cd nrg-parser
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev,test]
```
