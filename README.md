# My Personal Repo of Agents

## Local Development Environment

### Pre-requisites

1. Git
1. VSCode 
1. (Optional) Docker + VSCode Devcontainer extension

### If Not Using Dev Container

1. Python 3.13
1. Python Poetry 
`curl -sSL https://install.python-poetry.org | python3 -`

With current folder for this repo open in VSCode:

1. Launch VSCode command pallette `ctrl+P`
1. `>Python: Create Environment...`
1. Select the correct interpreter
1. Open Terminal in VSCode
1. Install dependencies in venv `poetry install`

### Launch Langgraph Server (Using Poetry)
`poetry run langgraph dev --debug-port 5678`
