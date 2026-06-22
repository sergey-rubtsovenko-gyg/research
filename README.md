# research

Collection of research Projects

# Jupyter + Databricks + Claude

## Usage

```
pyenv versions
pyenv activate jupyter-mcp

jupyter lab --port 8888 --IdentityProvider.token jupyter-mcp
```

## Install

### Databricks Connector

1. Use VsCode databricks extention to create a databricks connection.

2. Create a venv that is compatible with databricks running environment, use this venv in the databricks config in VsCode.

```
pip install ipykernel -U --force-reinstall
```

For displaying plotly plots and databricks execution progress
```
pip install plotly anywidget ipywidgets jupyterlab_widgets
```

3. After that one can execute `.ipynb` notebook cells on the databricks from the local machine.

### Claude Integration

Follow [this guide](https://www.reviewnb.com/claude-code-with-jupyter-notebooks) to install mcp for local jupyter server.

1. Install jupyter server
2. Install mcp for claude
3. Create a jupyter kernel with `.venv` that is connected to Databricks

```
python -m ipykernel install --user \
    --name "research-db" \
    --display-name "research-db"
```
4. Make sure you use `research-db` in jupyter and in claude code.
