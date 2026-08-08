"""
Damage severity rules: pixel-mask heuristics -> condition level (0-5) + confidence.

Each rule below only looks at binary pixel masks (this damage's own mask plus
other damage-type masks detected in the same crop/frame) - no numeric metadata,
no classifier score. That is why every rule always reports confidence="Low":
mask overlap alone is a weak signal for how severe the underlying damage is.

Level scale follows the same convention as bridge_health.py's C_HI: 5 = best
(no finding), 0 = worst. "Not found" (empty mask) is always level 5 for every
damage_type here.

damage_type -> rule summary (see docstring of each _rate_* for the exact logic):
  crack               overlaps rust -> 2, overlaps efflorescence -> 3,
                       no overlap -> 4, not found -> 5
  spalling            wide exposed-rebar overlap -> 1, point overlap -> 2,
                       no overlap -> 3, not found -> 5
  honeycomb           found -> 4, not found -> 5 (floor: never below 4)
  exposed_rebar       large rust overlap -> 2, otherwise -> 3, not found -> 5
  rust_efflorescence  (on concrete, not overlapping exposed rebar)
                       found -> 3, not found -> 5 (floor: never below 3)
  rust_on_rebar       (on steel, overlapping exposed rebar)
                       rebar + large crack overlap -> 1, rebar overlap only -> 2,
                       not found -> 5
"""

from dataclasses import dataclass

import numpy as np

# Fraction of this damage's own mask area that another mask must cover to count
# as "wide" / "large" overlap, as opposed to a single point / small overlap.
LARGE_OVERLAP_FRACTION = 0.3


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
    """Fraction of `mask`'s own area that overlaps `other`, in [0, 1]."""
    area = _area(mask)
    if area == 0:
        return 0.0
    return _overlap_area(mask, other) / area


def _apply_floor(level: int, floor: int) -> int:
    """Enforce 'must not be rated worse than `floor`' (higher number = better)."""
    return max(level, floor)


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
    if _area(mask) == 0:
        return 5
    return _apply_floor(4, floor=4)


def _rate_exposed_rebar(mask: np.ndarray, other_masks: dict) -> int:
    if _area(mask) == 0:
        return 5
    frac = _overlap_fraction(mask, other_masks.get("rust_mask"))
    if frac >= LARGE_OVERLAP_FRACTION:
        return 2
    # A small/point rust overlap isn't called out separately in the spec, so it
    # folds into the "no overlap" bucket below.
    return 3


def _rate_rust_efflorescence(mask: np.ndarray, other_masks: dict) -> int:
    """Rust+efflorescence stain on concrete, not overlapping exposed rebar."""
    if _area(mask) == 0:
        return 5
    return _apply_floor(3, floor=3)


def _rate_rust_on_rebar(mask: np.ndarray, other_masks: dict) -> int:
    """Rust on exposed steel - i.e. this mask overlaps exposed_rebar_mask."""
    if _area(mask) == 0:
        return 5
    if _overlap_area(mask, other_masks.get("exposed_rebar_mask")) > 0:
        crack_frac = _overlap_fraction(mask, other_masks.get("crack_mask"))
        if crack_frac >= LARGE_OVERLAP_FRACTION:
            return 1
        return 2
    # By definition this damage_type is rust found on exposed rebar, so this
    # mask should always overlap exposed_rebar_mask. If it doesn't (bad input),
    # fall back to the least severe defined outcome rather than guessing.
    return 2


_RULES = {
    "crack": _rate_crack,
    "spalling": _rate_spalling,
    "honeycomb": _rate_honeycomb,
    "exposed_rebar": _rate_exposed_rebar,
    "rust_efflorescence": _rate_rust_efflorescence,
    "rust_on_rebar": _rate_rust_on_rebar,
}


def rate_damage(damage_type: str, mask, other_masks_dict: dict | None = None) -> DamageRating:
    """
    Rate one damage instance's severity (0-5) from pixel masks alone.

    damage_type:      one of _RULES's keys, e.g. "crack", "spalling", ...
    mask:              this damage instance's own binary pixel mask
    other_masks_dict:  other damage types' masks in the same crop/frame, e.g.
                        {"rust_mask": ..., "efflorescence_mask": ...,
                         "exposed_rebar_mask": ..., "crack_mask": ...}
    """
    if damage_type not in _RULES:
        raise ValueError(f"unknown damage_type {damage_type!r}, expected one of {sorted(_RULES)}")
    level = _RULES[damage_type](_as_bool(mask), other_masks_dict or {})
    return DamageRating(level=level, confidence="Low")


if __name__ == "__main__":
    def _grid(rows: slice, cols: slice, shape=(10, 10)) -> np.ndarray:
        m = np.zeros(shape, dtype=bool)
        m[rows, cols] = True
        return m

    empty = np.zeros((10, 10), dtype=bool)

    # --- crack ---------------------------------------------------------
    crack_mask = _grid(slice(0, 5), slice(0, 5))          # 25 px, rows 0-4, cols 0-4
    rust_mask = _grid(slice(0, 2), slice(0, 2))           # overlaps crack
    efflor_mask = _grid(slice(3, 5), slice(3, 5))         # overlaps crack, no rust
    no_overlap_mask = _grid(slice(5, 7), slice(5, 7))     # doesn't touch crack

    r = rate_damage("crack", crack_mask, {"rust_mask": rust_mask, "efflorescence_mask": efflor_mask})
    assert r.level == 2 and r.confidence == "Low", r
    r = rate_damage("crack", crack_mask, {"rust_mask": empty, "efflorescence_mask": efflor_mask})
    assert r.level == 3 and r.confidence == "Low", r
    r = rate_damage("crack", crack_mask, {"rust_mask": no_overlap_mask, "efflorescence_mask": no_overlap_mask})
    assert r.level == 4 and r.confidence == "Low", r
    r = rate_damage("crack", empty, {"rust_mask": rust_mask})
    assert r.level == 5 and r.confidence == "Low", r
    print("[OK] crack")

    # --- spalling --------------------------------------------------------
    spalling_mask = _grid(slice(0, 10), slice(0, 4))              # 40 px (rows 0-9, cols 0-3)
    rebar_wide = _grid(slice(0, 10), slice(0, 2))                 # 20 px, all inside spalling -> 50%
    rebar_point = _grid(slice(0, 1), slice(0, 1))                 # 1 px inside spalling -> 2.5%
    rebar_none = _grid(slice(5, 7), slice(5, 7))                  # outside spalling entirely

    r = rate_damage("spalling", spalling_mask, {"exposed_rebar_mask": rebar_wide})
    assert r.level == 1 and r.confidence == "Low", r
    r = rate_damage("spalling", spalling_mask, {"exposed_rebar_mask": rebar_point})
    assert r.level == 2 and r.confidence == "Low", r
    r = rate_damage("spalling", spalling_mask, {"exposed_rebar_mask": rebar_none})
    assert r.level == 3 and r.confidence == "Low", r
    r = rate_damage("spalling", empty, {"exposed_rebar_mask": rebar_wide})
    assert r.level == 5 and r.confidence == "Low", r
    print("[OK] spalling")

    # --- honeycomb ---------------------------------------------------------
    honeycomb_mask = _grid(slice(0, 3), slice(0, 3))
    r = rate_damage("honeycomb", honeycomb_mask, {})
    assert r.level == 4 and r.confidence == "Low", r
    r = rate_damage("honeycomb", empty, {})
    assert r.level == 5 and r.confidence == "Low", r
    # floor: nothing in this rule can ever produce < 4 except "not found" (5)
    assert min(rate_damage("honeycomb", honeycomb_mask, {}).level, 5) >= 4
    print("[OK] honeycomb")

    # --- exposed_rebar -------------------------------------------------
    rebar_mask = _grid(slice(0, 10), slice(0, 4))                 # 40 px
    rust_large = _grid(slice(0, 10), slice(0, 2))                 # 20 px inside -> 50%
    rust_small = _grid(slice(0, 1), slice(0, 1))                  # 1 px inside -> 2.5%

    r = rate_damage("exposed_rebar", rebar_mask, {"rust_mask": rust_large})
    assert r.level == 2 and r.confidence == "Low", r
    r = rate_damage("exposed_rebar", rebar_mask, {"rust_mask": rust_small})
    assert r.level == 3 and r.confidence == "Low", r
    r = rate_damage("exposed_rebar", rebar_mask, {"rust_mask": empty})
    assert r.level == 3 and r.confidence == "Low", r
    r = rate_damage("exposed_rebar", empty, {"rust_mask": rust_large})
    assert r.level == 5 and r.confidence == "Low", r
    print("[OK] exposed_rebar")

    # --- rust_efflorescence (on concrete) -----------------------------
    stain_mask = _grid(slice(0, 3), slice(0, 3))
    r = rate_damage("rust_efflorescence", stain_mask, {})
    assert r.level == 3 and r.confidence == "Low", r
    r = rate_damage("rust_efflorescence", empty, {})
    assert r.level == 5 and r.confidence == "Low", r
    print("[OK] rust_efflorescence")

    # --- rust_on_rebar (on steel) ----------------------------------------
    rust_on_steel_mask = _grid(slice(0, 5), slice(0, 5))          # 25 px
    rebar_overlap = _grid(slice(0, 2), slice(0, 2))               # overlaps rust_on_steel_mask
    crack_large = _grid(slice(0, 5), slice(0, 5))                 # fully overlaps -> 100%
    crack_none = _grid(slice(6, 8), slice(6, 8))                  # no overlap

    r = rate_damage("rust_on_rebar", rust_on_steel_mask,
                     {"exposed_rebar_mask": rebar_overlap, "crack_mask": crack_large})
    assert r.level == 1 and r.confidence == "Low", r
    r = rate_damage("rust_on_rebar", rust_on_steel_mask,
                     {"exposed_rebar_mask": rebar_overlap, "crack_mask": crack_none})
    assert r.level == 2 and r.confidence == "Low", r
    r = rate_damage("rust_on_rebar", empty, {"exposed_rebar_mask": rebar_overlap})
    assert r.level == 5 and r.confidence == "Low", r
    print("[OK] rust_on_rebar")

    # --- unknown damage_type raises --------------------------------------
    try:
        rate_damage("not_a_real_type", empty, {})
        raise AssertionError("expected ValueError for unknown damage_type")
    except ValueError:
        pass
    print("[OK] unknown damage_type rejected")

    print("\n[OK] all damage_rules unit tests passed")
