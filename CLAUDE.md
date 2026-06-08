## Rules for Claude when working with Jupyter notebooks

### Launch

Connect to the kernel: `research-db` and use it for code execution in the notebook cells. 

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

