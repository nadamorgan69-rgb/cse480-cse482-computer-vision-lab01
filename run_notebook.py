"""Execute all notebook cells and save their outputs, from any working directory."""
import asyncio
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
root = Path(__file__).resolve().parent
path = root / 'Lab01_Computer_Vision.ipynb'
notebook = nbformat.read(path, as_version=4)
NotebookClient(notebook, timeout=300, kernel_name='python3',
               resources={'metadata': {'path': str(root)}}).execute()
assert all(cell.execution_count is not None for cell in notebook.cells if cell.cell_type == 'code')
nbformat.write(notebook, path)
print('All cells executed; notebook and results saved.')
