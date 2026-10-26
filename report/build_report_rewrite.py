"""Regenerate the illustrated report from the executed notebook results."""
from pathlib import Path
import json

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import CondPageBreak, Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/nadamorgan69-rgb/cse480-cse482-computer-vision-lab01"
COVER_IMAGE = ROOT / "images" / "computer_vision_dream_cover.png"
data = json.loads((ROOT / "results" / "verification.json").read_text())
assert all(status == "PASS" for status in data["checks"].values())
m = data["metrics"]

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="LabTitle", fontName="Helvetica-Bold", fontSize=18, leading=22,
    textColor=colors.black, spaceAfter=8, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="CoverSubheading", fontName="Helvetica-Bold", fontSize=16, leading=20,
    textColor=colors.black, spaceAfter=7, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="CoverBody", fontName="Helvetica", fontSize=12, leading=15,
    textColor=colors.HexColor("#1f2d38"), spaceAfter=5, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="LabBody", fontName="Helvetica", fontSize=12, leading=15.5,
    textColor=colors.HexColor("#1f2d38"), spaceAfter=8, alignment=TA_JUSTIFY,
))
styles.add(ParagraphStyle(
    name="LabCaption", fontName="Helvetica-Oblique", fontSize=12, leading=14.5,
    textColor=colors.HexColor("#465565"), spaceAfter=9, alignment=TA_CENTER,
))
styles["Heading1"].textColor = colors.black
styles["Heading1"].fontSize = 18
styles["Heading1"].leading = 22
styles["Heading1"].spaceBefore = 4
styles["Heading1"].spaceAfter = 7
styles["Heading1"].alignment = TA_JUSTIFY
styles["Heading2"].textColor = colors.black
styles["Heading2"].fontSize = 16
styles["Heading2"].leading = 20
styles["Heading2"].spaceBefore = 5
styles["Heading2"].spaceAfter = 4
styles["Heading2"].alignment = TA_JUSTIFY

story = []


def p(text, style="LabBody"):
    story.append(Paragraph(text, styles[style]))


def figure(relative_path, caption, width=440):
    path = ROOT / "results" / relative_path
    with PILImage.open(path) as im:
        w, h = im.size
    story.append(Image(str(path), width=width, height=width * h / w))
    p(caption, "LabCaption")


def table(rows, widths=None):
    t = Table(rows, colWidths=widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef3")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1f2d38")),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("LEADING", (0, 0), (-1, -1), 14.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#aab9c7")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#dce3e9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))


# Cover page
story.append(Spacer(1, 18))
p("Computer Vision Lab Assignment 01", "LabTitle")
p("CSE480 CSE482 Computer Vision Lab", "CoverSubheading")
p("Ain Shams University<br/>Mechatronics Engineering and Automation Program", "CoverBody")
with PILImage.open(COVER_IMAGE) as cover:
    cover_width, cover_height = cover.size
story.append(Spacer(1, 10))
story.append(Image(str(COVER_IMAGE), width=490, height=490 * cover_height / cover_width))
story.append(Spacer(1, 14))
p("<b>Student name</b>  Nada Said Yassin Morgan", "CoverBody")
p("<b>Student ID</b>  23P0284", "CoverBody")
story.append(PageBreak())

# Introduction and selective colour
p("How I approached the lab", "Heading2")
p(
    "I treated the four tasks as small experiments in how pixel values control an image. I kept the supplied "
    "images unchanged, performed every operation on NumPy arrays loaded by OpenCV, and used explicit "
    "BGR-to-RGB conversion only when displaying with Matplotlib. My aim was not only to obtain the requested "
    "pictures, but also to relate each visible change to the mask, weights, or channel assignments that produced it."
)

p("1. Selective Colour Isolation", "Heading1")
p(
    "I started by converting the apple image to grayscale because the unselected part of the final image needed "
    "brightness and texture without colour. I then separated the OpenCV image into blue, green, and red arrays. "
    "OpenCV stores them in BGR order, so naming the arrays correctly matters. A high red value alone is not enough "
    "to identify red-looking pixels: bright yellow areas can also contain a large red component. I therefore required "
    "R &gt;= 70, R-G &gt;= 30, R-B &gt;= 25, and G-B &lt;= 35. The differences were calculated with signed integers so "
    "that subtraction could not wrap around at 0 or 255. These values are image-specific thresholds: making the red "
    "differences larger would give a cleaner but smaller selection, while relaxing them would preserve more apple "
    "skin and also admit more orange or yellow background pixels."
)
figure(
    "task1/stages.png",
    "Figure 1. From left to right: the supplied image, grayscale brightness, red-channel intensity, the binary decision, the selected original pixels, and the final colour/grayscale composition.",
    width=438,
)
p(
    f"The white regions of the mask are the pixels that passed all four tests; the black regions failed at least "
    f"one test. In this result, {m['task1']['selected_percent']:.2f}% of the image is white. I used "
    "<b>bitwise_and</b> with the mask to keep original BGR values and used the inverted mask to take grayscale "
    "values everywhere else. Since the masks are complementary, <b>bitwise_or</b> joins the two parts without "
    "adding their intensities. Figure 1 shows why this is colour selection rather than apple detection. Red skin "
    "is retained, but yellow-green patches, highlights, stalks, and shadowed parts inside the same apples can turn "
    "gray when their channels do not meet the tests. The small red islands and gray holes follow local mottling in "
    "the fruit. The G-B condition rejects much of the orange ribbon, although a narrow red-dominant strip remains. "
    "Detecting complete apples would need spatial or object-level information, not only independent pixel tests."
)


# Page 2 - weighted overlay
story.append(CondPageBreak(220))
p("2. Creating a Ghostly Overlay", "Heading1")
p(
    "Weighted addition is performed at matching array positions, so both inputs first had to have the same height, "
    "width, number of channels, and data type. The cameraman already measured 225 x 225 pixels. I resized the "
    "425 x 313 zebra proportionally to 225 x 166, then added 29 white rows above it and 30 below it. This kept the "
    "whole zebra and avoided stretching its body. Both prepared inputs are therefore 225 x 225 uint8 BGR images. "
    "They share a canvas, but they are not geometrically registered because the subjects come from unrelated scenes."
)
p(
    "For each output location, <b>cv2.addWeighted()</b> calculates "
    "<b>I = alpha C + beta Z + gamma</b>. I used gamma = 0 and weights that sum to 1. Alpha controls the numerical "
    "contribution from the cameraman pixel and beta controls the zebra pixel at the same coordinate. This is more "
    "specific than saying that the weights change transparency: if a cameraman pixel has intensity 80 and the "
    "corresponding zebra pixel is 240, equal weights produce about 160 after rounding."
)
table([
    ["Experiment", "alpha: cameraman", "beta: zebra"],
    ["Cameraman dominant", "0.75", "0.25"],
    ["Equal contribution", "0.50", "0.50"],
    ["Zebra dominant", "0.25", "0.75"],
], [220, 140, 130])
figure(
    "task2/comparison.png",
    "Figure 2. The prepared inputs and the three pixel-by-pixel blends. The relative weights change both subject visibility and the overall background level.",
    width=440,
)
p(
    "In the 0.75/0.25 result, the cameraman, tripod, and horizon remain the main structure, while the zebra appears "
    "as a faint second exposure. At 0.50/0.50, the zebra stripes and the cameraman silhouette have similar visual "
    "strength, so neither scene reads as a clean foreground. At 0.25/0.75, the zebra becomes dominant and the "
    "cameraman looks pale behind it. Figure 2 also becomes progressively brighter as beta increases because most "
    "of the zebra image is white; those high pixel values are blended into the entire cameraman scene, not only the "
    "animal. The ghostly appearance is therefore the superposition of two semi-weighted subjects at the same pixel "
    "locations. A cleaner composite would require separating the zebra from its background and choosing a meaningful "
    "placement, but that would be a different operation from the requested full-image weighted overlay."
)


# Page 3 - vignette
story.append(CondPageBreak(220))
p("3. Artistic Vignette Filtering", "Heading1")
p(
    "I wanted attention to remain on the rover and nearby terrain while the frame edges became darker. I began with "
    "a one-channel black mask and drew a white circle at the image centre. White represents a multiplication weight "
    "near 1 and black represents a weight near 0. Applying that hard circle directly would cut brightness abruptly "
    "at its boundary and leave a visible circular edge, which would look like a cut-out rather than a vignette."
)
p(
    f"To turn the boundary into a gradual transition, I blurred the circle with a Gaussian filter. The radius is "
    f"{m['task3']['radius']} pixels, sigma is {m['task3']['sigma']:.1f} pixels, and the kernel is "
    f"{m['task3']['kernel_size']} x {m['task3']['kernel_size']}. I normalized the floating-point result so the maximum "
    "central value is 1. The blur creates every intermediate weight between the bright centre and dark exterior. "
    "For each channel I then calculated <b>V(y,x,c) = round(I(y,x,c) x W(y,x))</b>. A weight of 1 preserves the "
    "source value, 0.5 halves it, and a value close to 0 makes it almost black. The same weight is applied to B, G, "
    "and R, so the intended change is brightness rather than a colour shift."
)
figure(
    "task3/stages.png",
    "Figure 3. The hard circle defines the region of interest; Gaussian smoothing converts it into continuous weights, which darken the source progressively toward the frame edges.",
    width=432,
)
t3 = m["task3"]
table([
    ["Measured region", "Original mean", "Vignette mean"],
    ["Centre quarter, grayscale", f"{t3['center_before_mean']:.2f}", f"{t3['center_after_mean']:.2f}"],
    ["Four corner patches, grayscale", f"{t3['corner_before_mean']:.2f}", f"{t3['corner_after_mean']:.2f}"],
], [285, 102, 102])
p(
    f"The centre pixel stays unchanged, and the centre-quarter mean changes only from "
    f"{t3['center_before_mean']:.2f} to {t3['center_after_mean']:.2f}. By comparison, the corner mean falls from "
    f"{t3['corner_before_mean']:.2f} to {t3['corner_after_mean']:.2f}. This matches Figure 3: the rover body, wheels, "
    "arm, and central rock texture remain readable, while the corners and distant side terrain recede. A smaller "
    "circle would darken more of the rover; a larger one would retain more of the original frame. Increasing sigma "
    "would spread the transition farther, while decreasing it would make the circular boundary more obvious. A "
    "nonzero minimum weight could preserve additional corner detail, but the current near-black corners give the "
    "strong artistic framing requested."
)


# Page 4 - channel swapping on the zebra
story.append(CondPageBreak(220))
p("4. Channel Swapping - Zebra", "Heading1")
p(
    "A colour image contains three intensity values at every pixel. OpenCV stores those planes as blue, green, "
    "and red because its historical default is BGR rather than the RGB order normally used for display. Splitting "
    "the image does not create new colours; it exposes the three original intensity planes. Merging them in a new "
    "order changes which display colour receives each plane. For example, output BGR = (B,R,G) keeps blue in place, "
    "uses the original red values as green, and uses the original green values as red."
)
figure(
    "task4/comparison.png",
    "Figure 4. The original zebra and three exact channel permutations. The coat accents, muzzle, tail, and shadow change most; the neutral background and stripes change very little.",
    width=432,
)
rows = [["Output BGR", "Mean absolute change", "Maximum", "Changed pixels"]]
for row in m["task4"]["experiments"][:3]:
    rows.append([
        row["BGR_tuple"], f"{row['MAE']:.3f} / 255", str(row["max_difference"]),
        f"{row['changed_pixel_percent']:.2f}%",
    ])
table(rows, [120, 145, 90, 120])
p(
    f"The most noticeable changes in Figure 4 are the warm or cool tint around the ears and muzzle, the coloured "
    f"tail, and the pale ground shadow. The black stripes, white coat, and white background remain almost the same. "
    f"This happens because {m['task4']['neutral_zebra_percent']:.2f}% of the zebra pixels are exactly neutral, meaning "
    "B=G=R; any permutation of three equal numbers returns the same pixel. Many other pixels have channels that are "
    "only slightly different, so the changed-pixel percentages are around 45-51% even though the mean change is only "
    "1.41-2.36 intensity levels out of 255. The result is subtle for this particular source image, but it confirms an "
    "important point: channel swapping changes colour interpretation, not image geometry or brightness structure."
)


# Page 5 - stronger example, limitations, and conclusion
story.append(CondPageBreak(220))
p("Channel Swapping on the Mars Image", "Heading1")
p(
    "I repeated the same three assignments on the Mars rover image as a supplementary comparison. I did not add a "
    "tint or alter contrast; each result is still made only by reordering the original B, G, and R arrays."
)
figure(
    "task4/supplementary_marsrover.png",
    "Figure 5. The Mars scene makes the same permutations easier to see because the orange-brown terrain has strongly unequal channel values.",
    width=415,
)
rows = [["Output BGR", "Zebra mean change", "Mars mean change"]]
for zebra, mars in zip(m["task4"]["experiments"][:3], m["task4"]["experiments"][3:]):
    rows.append([zebra["BGR_tuple"], f"{zebra['MAE']:.3f}", f"{mars['MAE']:.3f}"])
table(rows, [190, 145, 145])
p(
    "The Mars differences are much stronger: (R,G,B) makes the ground blue, (B,R,G) makes it green, and (G,B,R) "
    "makes it magenta. Their mean absolute changes are 29.796, 18.264, and 11.737 levels, respectively, all much "
    "larger than for the zebra. The orange terrain originally contains more red than blue, so sending those unequal "
    "values to different output channels changes the perceived colour across most of the frame. Bright neutral rover "
    "panels still remain relatively stable. Comparing Figures 4 and 5 shows that a permutation is not inherently "
    "dramatic; its appearance depends on how similar or different the source channels are at each pixel."
)
story.append(CondPageBreak(260))
p("What I learned and what remains limited", "Heading2")
p(
    "The four results connect directly to their pixel operations. Complementary masks can combine colour and "
    "grayscale exactly, but a colour rule does not understand object boundaries. Weighted addition makes both "
    "images visible, but it also mixes their backgrounds. A blurred multiplication mask gives a controllable, "
    "smooth vignette, although its framing depends on radius and blur scale. Channel permutation preserves spatial "
    "detail while changing colour meaning, and neutral pixels expose why some images respond less than others. "
    "The executed notebook uses these same parameters and produces all five figures shown here; its assertions also "
    f"confirm the four task outputs and reopen all {data['png_count']} saved PNG files."
)
p(
    "<b>Project repository.</b> The notebook, source images, assignment, generated results, report builders, "
    "requirements, and final documents are available at "
    f'<link href="{REPOSITORY_URL}"><font color="#1f5f8b">{REPOSITORY_URL}</font></link>.'
)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#ccd6df"))
    canvas.line(48, 40, A4[0] - 48, 40)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#526576"))
    canvas.drawString(48, 28, "CSE480/CSE482 | Computer Vision Lab | Assignment #01")
    canvas.drawRightString(A4[0] - 48, 28, str(doc.page - 1))
    canvas.restoreState()


output = ROOT / "report" / "Lab01_Report.pdf"
doc = SimpleDocTemplate(
    str(output), pagesize=A4, rightMargin=48, leftMargin=48, topMargin=40, bottomMargin=54,
    title="Computer Vision Lab Assignment 01",
    author="Nada Said Yassin Morgan",
    pageCompression=1,
)
doc.build(story, onFirstPage=lambda canvas, document: None, onLaterPages=footer)
print(output)
