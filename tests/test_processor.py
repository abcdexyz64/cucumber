import numpy as np

from rotopixel.processor import RotoscopeSettings, process_image


def test_process_image_preserves_rgb_shape_for_small_frame():
    frame = np.zeros((32, 48, 3), dtype=np.uint8)
    frame[:, :24] = [240, 80, 64]
    frame[:, 24:] = [40, 160, 220]

    output = process_image(frame, RotoscopeSettings(max_width=64, pixel_size=2))

    assert output.shape == frame.shape
    assert output.dtype == np.uint8


def test_process_image_resizes_to_max_width():
    frame = np.zeros((80, 160, 3), dtype=np.uint8)

    output = process_image(frame, RotoscopeSettings(max_width=80, pixel_size=4))

    assert output.shape[:2] == (40, 80)


def test_stable_posterize_produces_limited_channel_values():
    gradient = np.linspace(0, 255, 64, dtype=np.uint8)
    frame = np.dstack([np.tile(gradient, (32, 1))] * 3)

    output = process_image(
        frame,
        RotoscopeSettings(
            palette="Stable Posterize",
            color_levels=4,
            pixel_size=1,
            edge_strength=0,
        ),
    )

    unique_values = np.unique(output[:, :, 0])
    assert len(unique_values) <= 4

