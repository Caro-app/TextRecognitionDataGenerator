import numpy as np
import cv2


def random_erosion(img: np.array, erosion_kernel_size: int, erosion_iteration: int, erosion_cap: float):
    """Random erosion
    Inputs: 
        img: np.array with 2 / 3 dimension
        erosion kernel_size: int
        erosion_iteration: int
        erosion_cap: max proportion of the image being eroded
    Returns:
        img: np.array with 2 / 3 dimension
    """
    if erosion_kernel_size == 0 or erosion_iteration == 0 or erosion_cap == 0:
        return img

    img = 255 - img
    kernel = np.ones((erosion_kernel_size, erosion_kernel_size),np.uint8)
    img_eroded = cv2.erode(img, kernel, iterations=erosion_iteration)

    p = min(np.random.random(), erosion_cap)

    if img.ndim == 2:
        random_mask = np.random.choice([0, 1], size=img.shape, p=[1 - p, p])
    elif img.ndim == 3:
        #random on pixel, not channel
        random_mask = np.random.choice([0, 1], size=img.shape[:2] , p=[1 - p, p])
        random_mask = np.expand_dims(random_mask, axis=2)
    blended = random_mask * img_eroded + (1 - random_mask) * img
    blended = 255 - blended
    return blended


def cutout(img: np.array, n_holes_pct: float, hole_size_pct: float):
    """Random cutoff
    Inputs: 
        img: np.array with 2 / 3 dimension
        n_holes_pct: Parameter controlling no of whole. If it is 1, it would cut out the longest dimension of the whole picture if the holes align on the same axis without overlap.
        hole_size_pct: Ratio of hole size to the minimum of height and width of picture
    Returns:
        img: np.array with 2 / 3 dimension
    """
    if n_holes_pct == 0 or hole_size_pct == 0:
        return img

    if img.ndim == 3:
        h, w = img.shape[0:2]
    elif img.ndim == 2:
        h, w = img.shape
    hole_size = int(min(h, w) * hole_size_pct)
    img = 255 - img
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
        mask[y1: y2, x1: x2] = 0

    if img.ndim == 3:
        mask = np.expand_dims(mask, axis=2)
    img = img * mask
    img = 255 - img
    return img