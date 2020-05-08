from ..data_generator import FakeTextDataGenerator
from ..utils import load_dict, load_fonts


class GeneratorFromStrings:
    """Generator that uses a given list of strings"""

    def __init__(
        self,
        strings,
        count=-1,
        fonts_en=[],
        fonts_ch=[],
        size=32,
        skewing_angle=0,
        random_skew=False,
        blur=0,
        random_blur=False,
        background_type=0,
        distorsion_type=0,
        distorsion_orientation=0,
        is_handwritten=False,
        width=-1,
        alignment=1,
        text_color="#282828",
        orientation=0,
        space_width=1.0,
        character_spacing=0,
        margins=(5, 5, 5, 5),
        random_margins=False,
        erosion_kernel_size=0,
        erosion_iteration=0,
        erosion_cap=0,
        n_holes_pct=0,
        hole_size_pct=0,
        alpha_low=255,
        invert=False,
        border_prob=0,
        border=(5, 5, 5, 5),
        fit=False,
        output_mask=False,
    ):
        self.count = count
        self.strings = strings
        self.fonts_en = fonts_en
        self.fonts_ch = fonts_ch
        self.size = size
        self.skewing_angle = skewing_angle
        self.random_skew = random_skew
        self.blur = blur
        self.random_blur = random_blur
        self.background_type = background_type
        self.distorsion_type = distorsion_type
        self.distorsion_orientation = distorsion_orientation
        self.is_handwritten = is_handwritten
        self.width = width
        self.alignment = alignment
        self.text_color = text_color
        self.orientation = orientation
        self.space_width = space_width
        self.character_spacing = character_spacing
        self.margins = margins
        self.random_margins = random_margins
        self.erosion_kernel_size = erosion_kernel_size
        self.erosion_iteration = erosion_iteration
        self.erosion_cap = erosion_cap 
        self.n_holes_pct = n_holes_pct
        self.hole_size_pct = hole_size_pct
        self.alpha_low = alpha_low
        self.invert = invert
        self.border_prob = border_prob
        self.border = border
        self.fit = fit
        self.output_mask = output_mask
        self.generated_count = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.generated_count == self.count:
            raise StopIteration
        self.generated_count += 1
        return (
            FakeTextDataGenerator.generate(
                self.generated_count,
                self.strings[(self.generated_count - 1) % len(self.strings)],
                self.fonts_en[(self.generated_count - 1) % len(self.fonts_en)],
                self.fonts_ch[(self.generated_count - 1) % len(self.fonts_ch)],
                None,
                self.size,
                None,
                self.skewing_angle,
                self.random_skew,
                self.blur,
                self.random_blur,
                self.background_type,
                self.distorsion_type,
                self.distorsion_orientation,
                self.is_handwritten,
                0,
                self.width,
                self.alignment,
                self.text_color,
                self.orientation,
                self.space_width,
                self.character_spacing,
                self.margins,
                self.random_margins,
                self.erosion_kernel_size,
                self.erosion_iteration,
                self.erosion_cap,
                self.n_holes_pct,
                self.hole_size_pct,
                self.alpha_low,
                self.invert,
                self.border_prob,
                self.border,
                self.fit,
                self.output_mask,
            ),
            self.strings[(self.generated_count - 1) % len(self.strings)],
        )