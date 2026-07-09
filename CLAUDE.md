## Rules for Claude when working with Jupyter notebooks

### Launch

- Connect to the kernel: `research-db` and use it for code execution in the notebook cells. 

- When I tell you to work in a certain notebook, you must use the kernel attached to the notebook. Find the notebook attached to the kernel using the following command:
    ```
    BASE="http://localhost:8001"
    TOKEN="jupyter-mcp"

    {
    echo "KERNEL_ID KERNEL_NAME NOTEBOOK"
    curl -s "$BASE/api/sessions?token=$TOKEN" \
        | jq -r '.[] | "\(.kernel.id) \(.kernel.name) \(.path)"'
    } | column -t
    ```
- When you connect to the kernel, print the name and the id of the kernel, you connected to.
- Cells in the notebook count from 0.

### Tool preference

- Use the Jupyter MCP for all `.ipynb` operations — read, edit, insert, delete, execute.
- Do not use your built-in `NotebookEdit` tool; it writes source as a single JSON string, which ruins standard Jupyter formatting.

### Outputs

- Never print secrets, API keys, tokens, or passwords into cell output.
- Large outputs consume tokens and fill up your context window. Prefer summaries (`.head()`, `.shape`) over dumping full DataFrames.

### Execution

- When installing packages, use `%pip install` inside the notebook (not `!pip install`) so packages install into the running kernel.
- Execute cells to verify they work. Do not assume the code is correct.
- If a cell errors, read the actual traceback before attempting a fix. Do not guess.
- Never overwrite the cell content if I didn't ask you explicitly to do that. Always add code to the new cell.
- When you are about to delete / change code, show me the diff in the console