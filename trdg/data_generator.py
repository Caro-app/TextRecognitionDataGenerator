import os
import random as rnd

from PIL import Image, ImageFilter, ImageOps

from trdg import computer_text_generator, background_generator, distorsion_generator, erosion_cutout
import numpy as np

try:
    from trdg import handwritten_text_generator
except ImportError as e:
    print("Missing modules for handwritten text generation.")


class FakeTextDataGenerator(object):
    @classmethod
    def generate_from_tuple(cls, t):
        """
            Same as generate, but takes all parameters as one tuple
        """

        cls.generate(*t)

    @classmethod
    def generate(
        cls,
        index,
        text,
        font_en,
        font_ch,
        out_dir,
        size,
        extension,
        skewing_angle,
        random_skew,
        blur,
        random_blur,
        background_type,
        distorsion_type,
        distorsion_orientation,
        is_handwritten,
        name_format,
        width,
        alignment,
        text_color,
        orientation,
        space_width,
        character_spacing,
        margins,
        random_margins,
        erosion_kernel_size,
        erosion_iteration,
        erosion_cap,
        n_holes_pct,
        hole_size_pct,
        border_prob,
        border,
        fit,
        output_mask,
    ):
        image = None
        margin_top, margin_left, margin_bottom, margin_right = margins
        if random_margins:
            margin_top = rnd.randint(0, margin_top)
            margin_left = rnd.randint(0, margin_left)
            margin_bottom = rnd.randint(0, margin_bottom)
            margin_right = rnd.randint(0, margin_right)

        horizontal_margin = margin_left + margin_right
        vertical_margin = margin_top + margin_bottom

        ##########################
        # Create picture of text #
        ##########################
        if is_handwritten:
            if orientation == 1:
                raise ValueError("Vertical handwritten text is unavailable")
            image = handwritten_text_generator.generate(text, text_color)
        else:
            image, mask = computer_text_generator.generate(
                text,
                font_en,
                font_ch,
                text_color,
                size,
                orientation,
                space_width,
                character_spacing,
                fit,
            )
        random_angle = rnd.randint(0 - skewing_angle, skewing_angle)

        rotated_img = image.rotate(
            skewing_angle if not random_skew else random_angle, expand=1
        )

        rotated_mask = mask.rotate(
            skewing_angle if not random_skew else random_angle, expand=1
        )

        #############################
        # Apply distorsion to image #
        #############################
        if distorsion_type == 0:
            distorted_img = rotated_img  # Mind = blown
            distorted_mask = rotated_mask
        elif distorsion_type == 1:
            distorted_img, distorted_mask = distorsion_generator.sin(
                rotated_img,
                rotated_mask,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2),
            )
        elif distorsion_type == 2:
            distorted_img, distorted_mask = distorsion_generator.cos(
                rotated_img,
                rotated_mask,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2),
            )
        else:
            distorted_img, distorted_mask = distorsion_generator.random(
                rotated_img,
                rotated_mask,
                vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2),
            )

        ##################################
        # Resize image to desired format #
        ##################################

        # Horizontal text
        if orientation == 0:
            new_width = int(
                distorted_img.size[0]
                * (float(size - vertical_margin) / float(distorted_img.size[1]))
            )
            resized_img = distorted_img.resize(
                (new_width, size - vertical_margin), Image.ANTIALIAS
            )
            resized_mask = distorted_mask.resize((new_width, size - vertical_margin))
            background_width = width if width > 0 else new_width + horizontal_margin
            background_height = size
        # Vertical text
        elif orientation == 1:
            new_height = int(
                float(distorted_img.size[1])
                * (float(size - horizontal_margin) / float(distorted_img.size[0]))
            )
            resized_img = distorted_img.resize(
                (size - horizontal_margin, new_height), Image.ANTIALIAS
            )
            resized_mask = distorted_mask.resize(
                (size - horizontal_margin, new_height), Image.ANTIALIAS
            )
            background_width = size
            background_height = new_height + vertical_margin
        else:
            raise ValueError("Invalid orientation")

        #############################
        # Generate background image #
        #############################
        if background_type == 0:
            background_img = background_generator.gaussian_noise(
                background_height, background_width
            )
        elif background_type == 1:
            background_img = background_generator.plain_white(
                background_height, background_width
            )
        elif background_type == 2:
            background_img = background_generator.quasicrystal(
                background_height, background_width
            )
        else:
            background_img = background_generator.picture(
                background_height, background_width
            )
        background_mask = Image.new("RGB", (background_width, background_height), (0, 0, 0))

        #############################
        # Place text with alignment #
        #############################

        new_text_width, _ = resized_img.size

        if alignment == 0 or width == -1:
            background_img.paste(resized_img, (margin_left, margin_top), resized_img)
            background_mask.paste(resized_mask, (margin_left, margin_top))
        elif alignment == 1:
            background_img.paste(
                resized_img,
                (int(background_width / 2 - new_text_width / 2), margin_top),
                resized_img,
            )
            background_mask.paste(
                resized_mask,
                (int(background_width / 2 - new_text_width / 2), margin_top),
            )
        else:
            background_img.paste(
                resized_img,
                (background_width - new_text_width - margin_right, margin_top),
                resized_img,
            )
            background_mask.paste(
                resized_mask,
                (background_width - new_text_width - margin_right, margin_top),
            )

        ##################################
        # Apply gaussian blur #
        ##################################

        gaussian_filter = ImageFilter.GaussianBlur(
            radius=blur if not random_blur else rnd.randint(0, blur)
        )
        final_image = background_img.filter(gaussian_filter)
        final_mask = background_mask.filter(gaussian_filter)

        ##################################
        # Apply random_erosion #
        ##################################
        final_image = np.array(final_image)
        final_mask = np.array(final_mask)

        ##################################
        # Apply random_erosion #
        ##################################
        final_image = erosion_cutout.random_erosion(final_image, erosion_kernel_size, erosion_iteration, erosion_cap)
        final_mask = erosion_cutout.random_erosion(final_mask, erosion_kernel_size, erosion_iteration, erosion_cap)

        ##################################
        # Apply Cutout #
        ##################################
        final_image = erosion_cutout.cutout(final_image, n_holes_pct, hole_size_pct)
        final_mask = erosion_cutout.cutout(final_mask, n_holes_pct, hole_size_pct)
        
        ##################################
        # Turning into PIL Image#
        ##################################
        final_image = Image.fromarray(np.uint8(final_image))
        final_mask = Image.fromarray(np.uint8(final_mask))

        ##################################
        # Add Border#
        ##################################
        if np.random.random() <= border_prob:
            border_size = (np.random.randint(1, border[0]) if border[0] > 0 else 0, 
                           np.random.randint(1, border[1]) if border[1] > 0 else 0, 
                           np.random.randint(1, border[2]) if border[2] > 0 else 0, 
                           np.random.randint(1, border[3]) if border[3] > 0 else 0)

            final_image = ImageOps.expand(final_image, border=border_size)
            final_mask = ImageOps.expand(final_mask, border=border_size)
        
        #####################################
        # Generate name for resulting image #
        #####################################
        if name_format == 0:
            image_name = "{}_{}.{}".format(text, str(index), extension)
            mask_name = "{}_{}_mask.png".format(text, str(index))
        elif name_format == 1:
            image_name = "{}_{}.{}".format(str(index), text, extension)
            mask_name = "{}_{}_mask.png".format(str(index), text)
        elif name_format == 2:
            image_name = "{}.{}".format(str(index), extension)
            mask_name = "{}_mask.png".format(str(index))
        else:
            print("{} is not a valid name format. Using default.".format(name_format))
            image_name = "{}_{}.{}".format(text, str(index), extension)
            mask_name = "{}_{}_mask.png".format(text, str(index))

        # Save the image
        if out_dir is not None:
            final_image.convert("RGB").save(os.path.join(out_dir, image_name))
            if output_mask == 1:
                final_mask.convert("RGB").save(os.path.join(out_dir, mask_name))
        else:
            if output_mask == 1:
                return final_image.convert("RGB"), final_mask.convert("RGB")
            return final_image.convert("RGB")
