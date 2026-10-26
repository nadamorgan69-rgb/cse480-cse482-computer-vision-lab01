"""Compatibility entry point for the expanded first-person lab report."""
from build_report_rewrite import *  # noqa: F401,F403
raise SystemExit

"""Legacy report generator retained below for reference."""
from pathlib import Path
import json
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'results' / 'verification.json').read_text())
assert all(status == 'PASS' for status in data['checks'].values())
m = data['metrics']
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='LabTitle', fontName='Helvetica-Bold', fontSize=20, leading=24,
                         textColor=colors.HexColor('#183b56'), spaceAfter=8))
styles.add(ParagraphStyle(name='LabBody', fontName='Helvetica', fontSize=10, leading=14, spaceAfter=8))
styles.add(ParagraphStyle(name='LabCaption', fontName='Helvetica-Oblique', fontSize=8.5,
                         leading=11, textColor=colors.HexColor('#465565'), spaceAfter=10))
styles['Heading1'].textColor = colors.HexColor('#183b56')
styles['Heading1'].fontSize = 15
styles['Heading1'].spaceAfter = 10
styles['Heading2'].fontSize = 11
styles['Heading2'].spaceBefore = 8
styles['Heading2'].spaceAfter = 5
story = []
def p(text, style='LabBody'):
    story.append(Paragraph(text, styles[style]))
def figure(relative_path, caption, width=490):
    path = ROOT / 'results' / relative_path
    with PILImage.open(path) as im:
        w, h = im.size
    story.append(Image(str(path), width=width, height=width*h/w))
    p(caption, 'LabCaption')
def table(rows, widths=None):
    t = Table(rows, colWidths=widths, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e8eef3')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('LEADING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor('#aab9c7')),
        ('LINEBELOW', (0,1), (-1,-1), 0.25, colors.HexColor('#dce3e9')),
        ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t)
    story.append(Spacer(1, 8))

p('Computer Vision Lab', 'LabTitle')
p('Assignment #01 | CSE480/CSE482<br/>Ain Shams University - Mechatronics Engineering and Automation', 'LabBody')
p('Introduction', 'Heading2')
p('This laboratory uses basic OpenCV operations to isolate color, blend images, create a smooth vignette, '
  'and permute color channels. All experiments use the supplied images. OpenCV processes BGR arrays; '
  'Matplotlib figures use an explicit BGR-to-RGB conversion. The executed notebook contains the complete code.')
p('1. Selective Colour Isolation', 'Heading1')
p('<b>Objective and method.</b> Preserve red apple regions and desaturate the rest. After grayscale conversion '
  'and cv2.split(), select pixels satisfying R &gt;= 70, R-G &gt;= 30, R-B &gt;= 25, and G-B &lt;= 35. '
  'Signed subtraction prevents uint8 wraparound. The green-blue limit reduces selection of the orange ribbon. '
  'cv2.bitwise_and() extracts original colors under the binary mask and grayscale under its inverse; '
  'cv2.bitwise_or() combines the disjoint regions.')
figure('task1/stages.png', 'Figure 1. Original image, grayscale, red channel, binary mask, extracted colors, and final composition.')
p(f'<b>Results and observations.</b> The mask selects {m["task1"]["selected_percent"]:.2f}% of the pixels. '
  'Red skins retain their original colors while yellow-green areas and the ribbon become mainly gray. '
  'Transitions within mottled skins remain visible because this is pixel-based color selection, not whole-object segmentation. '
  'Exact equality checks confirm original colors in selected pixels and equal gray channels everywhere else.')

story.append(PageBreak())
p('2. Creating a Ghostly Overlay', 'Heading1')
p('<b>Objective and method.</b> Blend cameraman.jpg (225 x 225) with zebra.png (425 x 313), using width x height. '
  'The zebra is resized proportionally to 225 x 166 and padded with 29 white rows above and 30 below. '
  'The cameraman remains 225 x 225. Both are uint8 BGR arrays on a common canvas; no content is cropped or stretched.')
p('<b>Equation:</b> I = alpha * C + beta * Z + gamma. Here gamma = 0 and alpha + beta = 1. '
  'Each result is computed with cv2.addWeighted().')
table([['Experiment', 'alpha (cameraman)', 'beta (zebra)'],
       ['First image dominant', '0.75', '0.25'], ['Equal blending', '0.50', '0.50'],
       ['Second image dominant', '0.25', '0.75']], [210, 145, 135])
figure('task2/comparison.png', 'Figure 2. Compatible inputs and all three transparency experiments.')
p('<b>Results and observations.</b> At alpha = 0.75 the cameraman is strongest; at beta = 0.75 the zebra is '
  'strongest. Equal blending gives comparable visibility to both silhouettes. The zebra\'s white background '
  'also brightens the scene, as expected from whole-image blending. These unrelated subjects are aligned '
  'to the same canvas rather than registered to matching scene features.')
p('<b>Verification.</b> All three outputs agree exactly with the independently calculated, rounded floating-point '
  'weighted sums (maximum difference: 0 intensity levels). They differ from both sources and from one another.')

story.append(PageBreak())
p('3. Artistic Vignette Filtering', 'Heading1')
p('<b>Objective and method.</b> Darken the edges of marsrover.png (853 x 480), retaining the center. '
  'A zero-valued single-channel mask receives a filled white circle using cv2.circle(). '
  f'The radius is {m["task3"]["radius"]} pixels. cv2.GaussianBlur() uses sigma = {m["task3"]["sigma"]:.1f} pixels '
  f'and a {m["task3"]["kernel_size"]} x {m["task3"]["kernel_size"]} kernel with constant-zero borders. '
  'The floating-point blurred mask is normalized to a maximum of 1.')
p('<b>Equation:</b> V(y,x,c) = round(I(y,x,c) * W(y,x)), with 0 &lt;= W &lt;= 1. '
  'The same weight multiplies all BGR channels; the clipped result is converted to uint8. '
  'The saved mask visualization is 8-bit, while the calculation uses the unquantized float weights.')
figure('task3/stages.png', 'Figure 3. The hard circle becomes a soft weighting mask and produces smooth edge darkening.')
t3 = m['task3']
table([['Region / measure', 'Original', 'Vignette'],
       ['Center quarter: mean grayscale', f'{t3["center_before_mean"]:.2f}', f'{t3["center_after_mean"]:.2f}'],
       ['Four corner patches: mean grayscale', f'{t3["corner_before_mean"]:.2f}', f'{t3["corner_after_mean"]:.2f}']], [300,95,95])
p('<b>Results and observations.</b> The central pixel is unchanged and the center quarter retains about '
  f'{100*t3["center_after_mean"]/t3["center_before_mean"]:.1f}% of its original average grayscale brightness. '
  'The four 10%-height by 10%-width corner patches become almost black. The transition is smooth, with no '
  f'hard circle visible; the largest adjacent weight change is {t3["max_adjacent_weight_step"]:.5f}. '
  'The wide frame has stronger side darkening. Shared channel weights preserve the color balance apart from rounding.')

story.append(PageBreak())
p('4. Channel Swapping - Zebra', 'Heading1')
p('<b>Objective and method.</b> Split zebra.png using cv2.split(), verify exact reconstruction with '
  'cv2.merge((B,G,R)), then merge three different permutations. Every tuple below names source channels '
  'assigned to (output blue, output green, output red). Thus (B,R,G) places original green data into output red.')
figure('task4/comparison.png', 'Figure 4. Required zebra experiment: original plus three exact channel permutations.', width=470)
rows = [['Output BGR tuple', 'MAE (0-255)', 'Max difference', 'Changed pixels']]
for row in m['task4']['experiments'][:3]:
    rows.append([row['BGR_tuple'], f'{row["MAE"]:.3f}', str(row['max_difference']),
                 f'{row["changed_pixel_percent"]:.2f}%'])
table(rows, [150,110,110,120])
p('<b>Results and observations.</b> The white background and black stripes remain largely neutral, '
  'while the tinted coat and shadow shift toward blue, green, or magenta. '
  f'Exactly {m["task4"]["neutral_zebra_percent"]:.2f}% of pixels have B=G=R and cannot change under any permutation. '
  'A large count of slightly changed pixels does not imply a large perceptual change: the mean absolute '
  'channel differences are only 1.41-2.36 levels out of 255.')
p('<b>Verification.</b> Every output channel matches its specified source channel exactly. Original '
  'reconstruction and neutral-pixel invariance pass. MAE is calculated across all pixels and all three channels '
  'using signed differences, avoiding overflow.')

story.append(PageBreak())
p('Supplementary Color Example and Conclusion', 'Heading1')
p('The same permutations are applied to the original Mars image, whose orange-brown terrain has more unequal '
  'BGR values. This supplements the required zebra experiment without replacing it.')
figure('task4/supplementary_marsrover.png', 'Figure 5. The Mars image makes the same channel assignments easier to see.', width=410)
rows = [['Output BGR tuple', 'Zebra MAE', 'Mars MAE']]
for z, mars in zip(m['task4']['experiments'][:3], m['task4']['experiments'][3:]):
    rows.append([z['BGR_tuple'], f'{z["MAE"]:.3f}', f'{mars["MAE"]:.3f}'])
table(rows, [230,130,130])
p('Verification', 'Heading2')
p(f'All four tasks passed the executed notebook assertions. All {data["png_count"]} saved PNGs reopen '
  'successfully; raw output arrays round-trip exactly. All six input arrays and source-file hashes remain '
  'unchanged. Masks, dtypes, dimensions, weighted arithmetic, center/corner brightness, and channel '
  'assignments are checked. The notebook includes nine embedded image figures. '
  'Comparisons were also inspected visually. Detailed measurements are saved in results/verification.json.')
p('Conclusion', 'Heading2')
p('Complementary binary masks combine original color with grayscale accurately. Weighted addition controls '
  'the visibility of two complete images. Gaussian smoothing turns a hard circle into continuous weights '
  'that produce a smooth vignette through multiplication. Channel order determines color interpretation, '
  'but neutral pixels remain unchanged. The observed strength of recoloring therefore depends on the source image.')
p('<b>Source and reproducibility.</b> Methods follow the supplied CSE480/CSE482 Lab Assignment #01 '
  '(assignment/lab01_tasks.pdf). README.md and requirements.txt provide run instructions and tested versions.')

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#ccd6df'))
    canvas.line(48, 40, A4[0]-48, 40)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#526576'))
    canvas.drawString(48, 28, 'CSE480/CSE482 | Computer Vision Lab | Assignment #01')
    canvas.drawRightString(A4[0]-48, 28, str(doc.page))
    canvas.restoreState()

output = ROOT / 'report' / 'Lab01_Report.pdf'
doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=48, leftMargin=48,
                        topMargin=42, bottomMargin=54, title='Computer Vision Lab - Assignment #01',
                        author='Mechatronics Engineering and Automation', pageCompression=1)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(output)
