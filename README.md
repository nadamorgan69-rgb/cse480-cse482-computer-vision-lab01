# Computer Vision Lab - Assignment #01

Ain Shams University, Mechatronics Engineering and Automation, CSE480/CSE482.
The main submission is **Lab01_Computer_Vision.ipynb**, executed with saved outputs.
The five-page **report/Lab01_Report.pdf** explains the actual experimental results in a natural first-person engineering voice.
An editable **report/Lab01_Report.docx** contains the same rewritten discussion and figures.

## Contents

- `Lab01_Computer_Vision.ipynb`: complete implementations, explanations, figures, and assertions.
- `images/`: all six original, unmodified source images; the two cats are validated but not task inputs.
- `assignment/lab01_tasks.pdf`: the supplied official assignment, copied without changes.
- `results/task1/` through `results/task4/`: intermediate images, final images, and labeled comparisons (38 PNGs).
- `results/verification.json`: measured results, task checks, input dimensions and SHA-256 hashes, and versions.
- `report/Lab01_Report.pdf`: illustrated report with method reasoning, result interpretation, and limitations.
- `report/Lab01_Report.docx`: editable Word version of the rewritten report.
- `report/build_report.py`: optional report regeneration from notebook results.
- `run_notebook.py`: optional headless execution of the full notebook.

## Run

Use Python 3.12 (tested with 3.12.14). Open a terminal in this project folder:

```text
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run_notebook.py
```

On macOS/Linux, activate with `source .venv/bin/activate` instead. The notebook runner
uses paths relative to its own location and executes the notebook with the project as
its working directory. It overwrites generated results and saves the executed notebook.

For interactive work, open the notebook in VS Code with the Jupyter extension, select
the environment above, and choose **Run All**. Alternatively install JupyterLab with
`python -m pip install jupyterlab` and run `python -m jupyterlab` from this folder.
All required images are local; no downloads are performed by the notebook.

To regenerate the report after executing the notebook:

```text
python report/build_report.py
```

## Tasks and observations

1. **Selective color:** red-channel thresholds and channel comparisons produce a binary mask;
   bitwise operations preserve original selected colors against grayscale. Selected pixels:
   54.52%. Thresholds are editable in the Task 1 cell. This is pixel color selection, so
   yellow-green areas within an apple also become gray. The green-blue gap helps reject the orange ribbon.
2. **Ghostly overlay:** cameraman is 225 x 225; zebra is resized from 425 x 313 to
   225 x 166, then padded with 29/30 white rows. Aspect ratio and full content are retained.
   Weights (0.75,0.25), (0.50,0.50), and (0.25,0.75) use gamma=0. The white zebra background
   also brightens the blended scene. Canvas alignment does not imply geometric registration.
3. **Vignette:** centered filled circle, radius 226; Gaussian sigma 91.2 and kernel 549 x 549;
   normalized float weights multiply the original. Center-quarter mean gray changes
   from 106.88 to 101.00, and corner mean from 138.67 to 0.91. The center pixel is unchanged.
4. **Channel swaps:** output BGR tuples (R,G,B), (B,R,G), and (G,B,R) are checked exactly.
   Zebra MAEs are 2.356, 1.408, and 1.714 intensity levels (out of 255). Exactly neutral
   pixels (46.47%) are unchanged. The supplementary Mars comparison produces larger MAEs
   of 29.796, 18.264, and 11.737. No artificial recoloring is added.

## Verification

- The complete notebook ran successfully: 6 code cells and 9 embedded image figures.
- All four task assertion groups passed; there are no notebook error outputs.
- Mask values/shapes, exact color/grayscale composition, all blend equations, vignette
  bounds/smoothness/darkening, and exact channel permutations were checked.
- The three blends matched independently rounded arithmetic with zero maximum error.
- All 38 PNGs reopened; processing outputs were also checked for exact save/reload equality.
- All project input files match the SHA-256 hashes recorded on first execution; source arrays were unchanged.
- Saved visual results and all report pages were inspected directly.

The project uses relative paths and includes its inputs. Jupyter may require permission
for localhost kernel communication; this is an environment requirement, not a limitation
of the algorithms. The six project images match the SHA-256 hashes of the supplied source
copies, and the assignment copy matches the original PDF in Downloads. No task remains
incomplete.
