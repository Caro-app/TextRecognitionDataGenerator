import numpy as np
import cv2


class DownstreamAugment:

    def __init__(self, img: np.ndarray, colormode: str):
        DownstreamAugment._color_channel_validate(img, colormode)
        self.img = img
        self.colormode = colormode

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, img):
        self._img = np.uint8(img)

    def get_img(self):
        return self.img
    
    def get_colormode(self):
        return self.colormode

    @staticmethod
    def _color_channel_validate(img: np.ndarray, colormode: str):
        if colormode != 'RGB' and colormode != 'RGBA':
            raise Exception('Colormode other than RGB and RGBA not supported')

        if colormode == 'RGB': 
            assert img.shape[-1] == 3
        elif colormode == 'RGBA':
            assert img.shape[-1] == 4

    def random_erosion(self,
                       erosion_kernel_size: int, 
                       erosion_iteration: int, 
                       erosion_cap: float):
        """Random erosion
        Inputs: 
            erosion kernel_size: int
            erosion_iteration: int
            erosion_cap: max proportion of the image being eroded
        """
        if erosion_kernel_size == 0 or erosion_iteration == 0 or erosion_cap == 0:
            return 

        img = self.img.copy() #img saved for later blend

        kernel = np.ones((erosion_kernel_size, erosion_kernel_size),np.uint8)

        if self.colormode == 'RGB':
            img = 255 - img
            img_eroded = cv2.erode(img, kernel, iterations=erosion_iteration)
        elif self.colormode == 'RGBA':
            img[:, :, :3] = 255 - img[:, :, :3]
            img_eroded = img.copy()
            img_eroded[:, :, :3] = cv2.erode(img[:, :, :3], kernel, iterations=erosion_iteration)

        p = min(np.random.random(), erosion_cap)

        #random on pixel, not channel
        random_mask = np.random.choice([0, 1], size=img.shape[:2] , p=[1 - p, p])
        random_mask = np.expand_dims(random_mask, axis=2)

        if self.colormode == 'RGB':
            blended = random_mask * img_eroded + (1 - random_mask) * img
            blended = 255 - blended
        elif self.colormode == 'RGBA':
            alpha = np.expand_dims(img[:, :, 3], axis=2)
            blended = random_mask * img_eroded[:, :, :3] + (1 - random_mask) * img[:, :, :3]
            blended = 255 - blended
            blended = np.concatenate([blended, alpha], axis=2)

        self.img = blended

    def cutout(self,
               n_holes_pct: float, 
               hole_size_pct: float):
        """Random cutoff
        Inputs: 
            n_holes_pct: Parameter controlling no of whole. If it is 1, it would cut out the longest dimension of the whole picture if the holes align on the same axis without overlap.
            hole_size_pct: Ratio of hole size to the minimum of height and width of picture
        Returns:
            img: np.array
        """
        if n_holes_pct == 0 or hole_size_pct == 0:
            return

        h, w = self.img.shape[0:2]
        hole_size = int(min(h, w) * hole_size_pct)
                
        mask = np.ones((h, w), np.uint8)
        n_holes_max = max(h, w) // hole_size * n_holes_pct
        n_holes = np.random.randint(n_holes_max)
        for _ in range(n_holes):
            # Central Anhor
            y = np.random.randint(h)
            x = np.random.randint(w)
            y1 = np.clip(y - hole_size // 2, 0, h)
            y2 = np.clip(y + hole_size // 2, 0, h)
            x1 = np.clip(x - hole_size // 2, 0, w)
            x2 = np.clip(x + hole_size // 2, 0, w)
            mask[y1: y2, x1: x2] = 255

        mask = np.expand_dims(mask, axis=2)

        if self.colormode == 'RGB':
            self.img = self.img * mask
        elif self.colormode == 'RGBA':
            self.img[:, :, :3] = self.img[:, :, :3] * mask

    def invert(self):
        if self.colormode == 'RGB':
            self.img = cv2.bitwise_not(self.img)
        elif self.colormode == 'RGBA':
            self.img[:, :, :3] = cv2.bitwise_not(self.img[:, :, :3])

    def transparentify(self,
                       low: int=100, 
                       high: int=255):
        assert low >= 0 
        assert high <= 255

        if self.colormode == 'RGBA':
            pass
        elif self.colormode == 'RGB':
            self.img = cv2.cvtColor(self.img, cv2.COLOR_RGB2RGBA)
            self.colormode = 'RGBA'
        else:
            raise Exception('Colormode other than RGB and RGBA not supported')

        self.img[:, :, 3] = np.random.randint(low, high=high)
