"""Replace notebook markdown while leaving all executable cells unchanged."""
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Lab01_Computer_Vision.ipynb"


def source(text):
    return text.strip().splitlines(keepends=True)


replacements = {
    0: r"""
# Computer Vision Lab - Assignment #01
**Ain Shams University | Mechatronics Engineering and Automation | CSE480/CSE482**

In this notebook I work through four image-processing tasks using the supplied images. I focus on the link between the arithmetic performed on the BGR arrays and what is visible in each result: a colour mask for the apples, weighted addition for the ghostly overlay, a smooth multiplication mask for the vignette, and channel permutations for the surreal-colour experiment. I keep the source files unchanged and save every generated stage under `results/`.

OpenCV loads colour data in **BGR** order, while Matplotlib expects **RGB** for display. I therefore keep the processing arrays in BGR and convert only the copies passed to plotting functions. The final section checks the output relationships numerically so that the explanations and figures refer to the same executed implementation.
""",
    2: r"""
## Task 1 - Selective Colour Isolation

My aim is to keep red-dominant pixels in their original colour while showing the rest of the apple image in grayscale. I first create the grayscale version because it preserves brightness, edges, and fruit texture without retaining hue. I also split the original image into blue, green, and red planes. Since OpenCV returns them as B, G, R, the variable order is important.

A large red value by itself would also include bright yellow and orange pixels, so I use comparisons between the channels. The final condition is **R >= 70, R-G >= 30, R-B >= 25, and G-B <= 35**. The intensity floor removes very dark pixels, the two red-dominance gaps require red to be clearly stronger, and the green-blue limit reduces selection of the orange ribbon. I cast the channels to signed integers before subtraction because subtraction on `uint8` can wrap around and reverse the intended comparison.

Pixels that pass all four tests receive 255 in the binary mask and appear white; pixels that fail receive 0 and appear black. These thresholds are specific to this image. Tightening the red-dominance gaps would give fewer, purer red pixels, while relaxing them would keep more of the apple skins but also accept more yellow-orange areas. This is a pixel rule rather than semantic apple segmentation.
""",
    4: r"""
The binary mask selects **54.52%** of the image. I use `bitwise_and` with that mask to extract the selected original BGR pixels. I invert the mask and use it to extract the complementary pixels from the three-channel grayscale image. Because the two masks do not overlap, `bitwise_or` can join the colour and grayscale parts without adding their intensities.

In the stage figure, the central and lower red apples keep large areas of colour, while the yellow-green apples and highlights are mostly gray. The selection is visibly patchy inside several apples: local yellow mottling, bright reflections, stalks, and shadowed skin do not satisfy the same channel relationships as the red skin around them. Those gray holes are therefore consistent with the threshold logic rather than an error in the bitwise composition. A narrow red-dominant part of the ribbon is also retained even though it is not an apple. This is the main limitation of the method: it identifies pixels with a chosen colour signature, not complete objects with boundaries. Whole-apple detection would need spatial grouping, shape information, or an object segmentation method.
""",
    5: r"""
## Task 2 - Creating a Ghostly Overlay

`cv2.addWeighted()` combines values at matching pixel coordinates, so the inputs must have identical dimensions, compatible channel formats, and the same data type. The cameraman image is already **225 x 225**. The zebra is **425 x 313**, so I resize it proportionally to **225 x 166** and add 29 white rows above and 30 below. This keeps the complete zebra and avoids stretching it. Both prepared inputs are then 225 x 225, three-channel, `uint8` BGR arrays. They share a canvas, although the two unrelated scenes are not geometrically registered.

For every coordinate and channel, the operation is

**output = alpha x cameraman + beta x zebra + gamma**

with `gamma = 0` and `alpha + beta = 1`. Alpha is the numerical contribution of the cameraman pixel and beta is the contribution of the zebra pixel. For example, equal weights turn values 80 and 240 at the same location into approximately 160 after rounding. The weights therefore control which image contributes more strongly at every pixel, not a separate object-level transparency.
""",
    7: r"""
The three figures have distinct appearances. At **alpha=0.75, beta=0.25**, the cameraman, tripod, and horizon remain dominant and the zebra looks like a faint second exposure. At **0.50, 0.50**, the zebra stripes and cameraman silhouette have similar strength, so neither scene reads as a clean foreground. At **0.25, 0.75**, the zebra becomes the clearest subject and the cameraman is pale behind it.

The background also changes, not only the two subjects. Most of the zebra image is white, so increasing beta blends high intensity values into the entire cameraman scene and makes the result brighter. The ghostly look comes from superimposing two semi-weighted subjects at the same coordinates while their backgrounds are mixed as well. A cleaner composite would require removing the zebra background and placing its foreground deliberately, but that would be different from the requested whole-image weighted blend. The independent arithmetic check below confirms that all three saved results match the rounded per-pixel equations exactly.
""",
    8: r"""
## Task 3 - Artistic Vignette Filtering

I want to keep attention on the rover and the nearby terrain while progressively darkening the frame edges. I start with a single-channel black mask and draw a filled white circle at the image centre. In a multiplication mask, white corresponds to a weight near 1 and black to a weight near 0. If I multiplied the image by this hard circle directly, the brightness would stop abruptly at the circumference and leave an obvious circular cut-out.

I therefore blur the circle with a Gaussian filter. The radius is **0.47 x min(height, width) = 226 pixels**, and the Gaussian sigma is **0.19 x min(height, width) = 91.2 pixels** with a 549 x 549 kernel. Blurring replaces the two mask values with a continuous range; after normalization, the brightest centre is 1 and the surrounding weights approach 0. I calculate

**output(y,x,c) = round(input(y,x,c) x weight(y,x))**

for each BGR channel. A weight of 1 preserves a pixel, 0.5 halves its intensity, and a value close to 0 makes it almost black. I keep the mask in floating point during multiplication so those intermediate weights are not lost.
""",
    10: r"""
The hard-mask panel explains where the centre region comes from, while the smooth-mask panel shows why no sharp circle appears in the final image. The centre pixel is unchanged. The mean grayscale value of the centre quarter changes only from **106.88 to 101.00**, whereas the four corner patches fall from **138.67 to 0.91**. Visually, the rover body, wheels, arm, and central rock texture remain readable, while the corners and distant side terrain recede. Applying the same weight to all three channels changes brightness without deliberately shifting hue, apart from small `uint8` rounding effects.

The result depends on the mask parameters. A smaller radius would darken more of the rover; a larger radius would retain more of the original frame. Increasing sigma would spread the transition farther, while a smaller sigma would make the circle boundary more noticeable. Introducing a nonzero minimum weight would preserve more corner detail. I did not add such a floor here because the near-black corners give the strong artistic framing requested, while the central subject still retains sufficient detail.
""",
    11: r"""
## Task 4 - Channel Swapping (Surreal Colours)

A colour pixel has three intensity values. OpenCV stores them as **blue, green, red**, so splitting an image exposes three two-dimensional intensity planes. Merging those same planes as `(B,G,R)` reconstructs the source exactly. Merging them in another order does not move any pixel or invent a new value; it changes which display colour receives each original plane.

Every tuple below lists the source planes assigned to **(output blue, output green, output red)**:

| Arrangement | Output B | Output G | Output R |
|---|---|---|---|
| Original (B,G,R) | B | G | R |
| Swap 1 (R,G,B) | R | G | B |
| Swap 2 (B,R,G) | B | R | G |
| Swap 3 (G,B,R) | G | B | R |

For example, `(B,R,G)` keeps the blue plane in place, displays original red values as green, and displays original green values as red. A grayscale pixel has B=G=R, so permuting three equal numbers cannot change it. This predicts that the zebra's black stripes and white background will be far less affected than its tinted coat, muzzle, tail, and shadow.
""",
    13: r"""
The zebra results match that prediction. The cooler, greener, or magenta tint is easiest to see around the ears and muzzle, along the tail, and in the pale ground shadow. The black stripes, white coat, and background remain almost unchanged. Exactly **46.47%** of the zebra pixels have B=G=R and are invariant under every permutation. Although roughly 45-51% of pixels change in the three outputs, their mean absolute channel changes are only **2.356, 1.408, and 1.714** levels out of 255. A high changed-pixel count therefore does not imply a strong visible recolouring when the original channels differ by only a few levels.

I use the Mars rover as a supplementary comparison with exactly the same channel assignments. Its orange-brown terrain contains much more red than blue, so the permutations turn the scene strongly blue, green, or magenta. The corresponding mean changes are **29.796, 18.264, and 11.737**, much larger than for the zebra. This comparison shows that channel swapping changes colour interpretation while preserving spatial structure, and that the visual strength of the result depends on how unequal the source channels already are.
""",
    14: r"""
## Final checks

The checks below connect the displayed results to the arrays that produced them. They verify the complementary mask composition, the three weighted-addition equations, the vignette bounds and brightness change, and every requested channel assignment. They also reopen each saved PNG and confirm that the supplied input arrays and source bytes were not modified. These checks support the observations above without replacing the visual interpretation of the figures.
""",
    16: r"""
## Conclusion

The four tasks gave me different ways to control an image at pixel level. In Task 1, complementary masks combine selected original colour with grayscale exactly, but the patchy apples show that a colour threshold has no understanding of object boundaries. In Task 2, normalized weights control the contribution of two complete images, including their backgrounds, which explains both the ghostly subjects and the brightening caused by the zebra's white canvas. In Task 3, Gaussian smoothing turns a binary circle into continuous multiplication weights, preserving central detail while gradually suppressing the edges. In Task 4, channel order changes the meaning of the stored values; neutral pixels remain stable, while a strongly coloured source such as the Mars scene changes dramatically.

The main trade-off across the lab is that simple array operations are predictable and easy to verify, but their visual result depends strongly on the content of the source images and the chosen parameters. The executed notebook and the report use the same thresholds, blend weights, vignette settings, permutations, and generated figures.
""",
}


notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
for index, text in replacements.items():
    cell = notebook["cells"][index]
    if cell["cell_type"] != "markdown":
        raise ValueError(f"Cell {index} is not markdown")
    cell["source"] = source(text)

NOTEBOOK.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Updated {len(replacements)} markdown cells in {NOTEBOOK}")
