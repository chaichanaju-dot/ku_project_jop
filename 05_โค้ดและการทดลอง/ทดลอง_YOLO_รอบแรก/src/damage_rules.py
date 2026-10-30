# Pixel-mask overlap heuristics -> condition level (0-5, 5=best) + confidence.
# `level` is a same-type-overlap proxy for severity (no pixel-to-mm scale available yet),
# `confidence` is only the OBB damage model's own detection confidence - the two are independent.

from dataclasses import dataclass

import numpy as np

LARGE_OVERLAP_FRACTION = 0.3
HIGH_CONF_THRESHOLD = 0.5


@dataclass
class DamageRating:
    level: int
    confidence: str


def _as_bool(mask) -> np.ndarray:
    return np.asarray(mask).astype(bool)


def _area(mask: np.ndarray) -> int:
    return int(np.count_nonzero(mask))


def _overlap_area(mask_a: np.ndarray, mask_b: np.ndarray | None) -> int:
    if mask_b is None:
        return 0
    return int(np.count_nonzero(mask_a & _as_bool(mask_b)))


def _overlap_fraction(mask: np.ndarray, other: np.ndarray | None) -> float:
    area = _area(mask)
    if area == 0:
        return 0.0
    return _overlap_area(mask, other) / area


def _rate_crack(mask: np.ndarray, other_masks: dict) -> int:
    if _area(mask) == 0:
        return 5
    if _overlap_area(mask, other_masks.get("rust_mask")) > 0:
        return 2
    if _overlap_area(mask, other_masks.get("efflorescence_mask")) > 0:
        return 3
    return 4


def _rate_spalling(mask: np.ndarray, other_masks: dict) -> int:
    if _area(mask) == 0:
        return 5
    frac = _overlap_fraction(mask, other_masks.get("exposed_rebar_mask"))
    if frac >= LARGE_OVERLAP_FRACTION:
        return 1
    if frac > 0:
        return 2
    return 3


def _rate_honeycomb(mask: np.ndarray, other_masks: dict) -> int:
    return 5 if _area(mask) == 0 else 4


def _rate_exposed_rebar(mask: np.ndarray, other_masks: dict) -> int:
    if _area(mask) == 0:
        return 5
    frac = _overlap_fraction(mask, other_masks.get("rust_mask"))
    return 2 if frac >= LARGE_OVERLAP_FRACTION else 3


def _rate_rust_efflorescence(mask: np.ndarray, other_masks: dict) -> int:
    return 5 if _area(mask) == 0 else 3


def _rate_rust_on_rebar(mask: np.ndarray, other_masks: dict) -> int:
    if _area(mask) == 0:
        return 5
    if _overlap_area(mask, other_masks.get("exposed_rebar_mask")) > 0:
        crack_frac = _overlap_fraction(mask, other_masks.get("crack_mask"))
        return 1 if crack_frac >= LARGE_OVERLAP_FRACTION else 2
    return 2


_RULES = {
    "crack": _rate_crack,
    "spalling": _rate_spalling,
    "honeycomb": _rate_honeycomb,
    "exposed_rebar": _rate_exposed_rebar,
    "rust_efflorescence": _rate_rust_efflorescence,
    "rust_on_rebar": _rate_rust_on_rebar,
}


def rate_damage(
    damage_type: str,
    mask,
    other_masks_dict: dict | None = None,
    det_conf: float | None = None,
) -> DamageRating:
    if damage_type not in _RULES:
        raise ValueError(f"unknown damage_type {damage_type!r}, expected one of {sorted(_RULES)}")
    level = _RULES[damage_type](_as_bool(mask), other_masks_dict or {})
    confidence = "High" if det_conf is not None and det_conf >= HIGH_CONF_THRESHOLD else "Low"
    return DamageRating(level=level, confidence=confidence)


if __name__ == "__main__":
    def _grid(rows: slice, cols: slice, shape=(10, 10)) -> np.ndarray:
        m = np.zeros(shape, dtype=bool)
        m[rows, cols] = True
        return m

    empty = np.zeros((10, 10), dtype=bool)

    crack_mask = _grid(slice(0, 5), slice(0, 5))
    rust_mask = _grid(slice(0, 2), slice(0, 2))
    efflor_mask = _grid(slice(3, 5), slice(3, 5))
    no_overlap_mask = _grid(slice(5, 7), slice(5, 7))

    assert rate_damage("crack", crack_mask, {"rust_mask": rust_mask, "efflorescence_mask": efflor_mask}).level == 2
    assert rate_damage("crack", crack_mask, {"rust_mask": empty, "efflorescence_mask": efflor_mask}).level == 3
    assert rate_damage("crack", crack_mask, {"rust_mask": no_overlap_mask, "efflorescence_mask": no_overlap_mask}).level == 4
    assert rate_damage("crack", empty, {"rust_mask": rust_mask}).level == 5
    print("[OK] crack")

    spalling_mask = _grid(slice(0, 10), slice(0, 4))
    rebar_wide = _grid(slice(0, 10), slice(0, 2))
    rebar_point = _grid(slice(0, 1), slice(0, 1))
    rebar_none = _grid(slice(5, 7), slice(5, 7))

    assert rate_damage("spalling", spalling_mask, {"exposed_rebar_mask": rebar_wide}).level == 1
    assert rate_damage("spalling", spalling_mask, {"exposed_rebar_mask": rebar_point}).level == 2
    assert rate_damage("spalling", spalling_mask, {"exposed_rebar_mask": rebar_none}).level == 3
    assert rate_damage("spalling", empty, {"exposed_rebar_mask": rebar_wide}).level == 5
    print("[OK] spalling")

    honeycomb_mask = _grid(slice(0, 3), slice(0, 3))
    assert rate_damage("honeycomb", honeycomb_mask, {}).level == 4
    assert rate_damage("honeycomb", empty, {}).level == 5
    print("[OK] honeycomb")

    rebar_mask = _grid(slice(0, 10), slice(0, 4))
    rust_large = _grid(slice(0, 10), slice(0, 2))
    rust_small = _grid(slice(0, 1), slice(0, 1))

    assert rate_damage("exposed_rebar", rebar_mask, {"rust_mask": rust_large}).level == 2
    assert rate_damage("exposed_rebar", rebar_mask, {"rust_mask": rust_small}).level == 3
    assert rate_damage("exposed_rebar", rebar_mask, {"rust_mask": empty}).level == 3
    assert rate_damage("exposed_rebar", empty, {"rust_mask": rust_large}).level == 5
    print("[OK] exposed_rebar")

    stain_mask = _grid(slice(0, 3), slice(0, 3))
    assert rate_damage("rust_efflorescence", stain_mask, {}).level == 3
    assert rate_damage("rust_efflorescence", empty, {}).level == 5
    print("[OK] rust_efflorescence")

    rust_on_steel_mask = _grid(slice(0, 5), slice(0, 5))
    rebar_overlap = _grid(slice(0, 2), slice(0, 2))
    crack_large = _grid(slice(0, 5), slice(0, 5))
    crack_none = _grid(slice(6, 8), slice(6, 8))

    assert rate_damage("rust_on_rebar", rust_on_steel_mask, {"exposed_rebar_mask": rebar_overlap, "crack_mask": crack_large}).level == 1
    assert rate_damage("rust_on_rebar", rust_on_steel_mask, {"exposed_rebar_mask": rebar_overlap, "crack_mask": crack_none}).level == 2
    assert rate_damage("rust_on_rebar", empty, {"exposed_rebar_mask": rebar_overlap}).level == 5
    print("[OK] rust_on_rebar")

    try:
        rate_damage("not_a_real_type", empty, {})
        raise AssertionError("expected ValueError for unknown damage_type")
    except ValueError:
        pass
    print("[OK] unknown damage_type rejected")

    assert rate_damage("crack", crack_mask, {"rust_mask": rust_mask}, det_conf=0.83).confidence == "High"
    assert rate_damage("crack", crack_mask, {"rust_mask": rust_mask}, det_conf=0.5).confidence == "High"
    assert rate_damage("crack", crack_mask, {"rust_mask": rust_mask}, det_conf=0.2).confidence == "Low"
    assert rate_damage("crack", crack_mask, {"rust_mask": rust_mask}, det_conf=None).confidence == "Low"
    print("[OK] det_conf")

    print("\n[OK] all damage_rules unit tests passed")
