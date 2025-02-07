# My Personal Repo of Agents

## Local Development Setup

### Pre-requisites

1. Git
1. VSCode 
1. (Optional) Docker + VSCode Devcontainer extension

### Setup Python and Poetry

1. [Install pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)
1. Install python 3.13.1 `pyenv install 3.13.1`
1. Activate python `pyenv global 3.13.1`
1. Install poetry `pip install poetry`
1. Install required packages `poetry install`
1. Determine path to interpreter `poetry env info --path`

### Setup VS Code
With current folder for this repo open in VSCode:

1. Install Python and Pylance extensions
1. Launch VSCode command pallette `ctrl+P`
1. `>Python: Select Interpreter...`
1. Enter interpreter path provided by poetry

## Launch local Mongo instance
From terminal where working directory is root of this repo
1. `docker compose up`

## Debug via Local Langgraph Server
1. Launch langgraph server: `poetry run langgraph dev --debug-port 5678`
1. Connect VSCode to server using: `Attach to LangGraph server`

## Rebuild Poetry Environment
1. `poetry env remove $(poetry env list | grep Activated | awk '{print $1}')`
1. `poetry install`


