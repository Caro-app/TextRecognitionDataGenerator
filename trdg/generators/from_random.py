from .from_strings import GeneratorFromStrings
from ..data_generator import FakeTextDataGenerator
from ..string_generator import create_strings_randomly, ControlledRandomStringsGenerator
from ..utils import load_dict, load_fonts


class GeneratorFromRandom:
    """Generator that uses randomly generated words"""

    def __init__(
        self,
        count=-1,
        length=1,
        allow_variable=False,
        use_letters=True,
        use_numbers=True,
        use_symbols=True,
        fonts_en=[],
        fonts_ch=[],
        language='en',
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
        fit=False,
        output_mask=False,
    ):
        self.count = count
        self.length = length
        self.allow_variable = allow_variable
        self.use_letters = use_letters
        self.use_numbers = use_numbers
        self.use_symbols = use_symbols
        self.language = language
        self.generator = GeneratorFromStrings(
            create_strings_randomly(
                self.length,
                self.allow_variable,
                1000,
                self.use_letters,
                self.use_numbers,
                self.use_symbols,
                self.language,
            ),
            count,
            fonts_en,
            fonts_ch,
            size,
            skewing_angle,
            random_skew,
            blur,
            random_blur,
            background_type,
            distorsion_type,
            distorsion_orientation,
            is_handwritten,
            width,
            alignment,
            text_color,
            orientation,
            space_width,
            character_spacing,
            margins,
            random_margins,
            fit,
            output_mask,
        )

    def __iter__(self):
        return self.generator

    def __next__(self):
        return self.next()

    def next(self):
        if self.generator.generated_count >= 999:
            self.generator.strings = create_strings_randomly(
                self.length,
                self.allow_variable,
                1000,
                self.use_letters,
                self.use_numbers,
                self.use_symbols,
                self.language,
            )
        return self.generator.next()


class GeneratorFromControlledRandom:
    """Generator that uses randomly generated words"""

    def __init__(
        self,
        count=-1,
        length=20,
        allow_variable=False,
        lang_mix={'cn': 0.35, 'en': 0.4, 'num': 0.2, 'sym': 0.05},
        next_lang_stickness=0.7,
        space_probability=0.3,
        ch_file=None,
        en_file=None,
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
        fit=False,
        output_mask=False,
    ):
        self.count = count
        self.length = length
        self.allow_variable = allow_variable
        self.lang_mix = lang_mix
        self.next_lang_stickness = next_lang_stickness
        self.space_probability = space_probability
        self.ch_file = ch_file
        self.en_file = en_file
        self.texts_gen = ControlledRandomStringsGenerator(self.length,
                                                          self.allow_variable, 
                                                          1000, 
                                                          self.lang_mix, 
                                                          self.next_lang_stickness,
                                                          self.space_probability,
                                                          ch_file=self.ch_file, 
                                                          en_file=self.en_file)
        self.generator = GeneratorFromStrings(
            self.texts_gen.generate(),
            count,
            fonts_en,
            fonts_ch,
            size,
            skewing_angle,
            random_skew,
            blur,
            random_blur,
            background_type,
            distorsion_type,
            distorsion_orientation,
            is_handwritten,
            width,
            alignment,
            text_color,
            orientation,
            space_width,
            character_spacing,
            margins,
            random_margins,
            fit,
            output_mask,
        )

    def __iter__(self):
        return self.generator

    def __next__(self):
        return self.next()

    def next(self):
        if self.generator.generated_count >= 999:
            self.generator.strings = self.texts_gen.generate()
        return self.generator.next()
