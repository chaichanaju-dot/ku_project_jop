"""
T-BHI (Thai Bridge Health Index) calculator.

Implements the scoring pipeline from
"คู่มือเริ่มต้นโปรเจกต์ประเมินสะพานจากภาพโดรน", sections 4.4, 4.6, 4.7, 4.8:

  4.4  C_hi  - condition level (0-5) -> health coefficient (0.00-1.00)
  4.6  EHI   = sum(C_hi * proportion_of_area) * 100          (per element)
       T-BHI = sum(q * W * EHI) / sum(q * W)                 (whole bridge)
  4.7  Worked example used here as the regression check (T-BHI = 96.99)
  4.8  T-BHI -> status band, THEN the mandatory rule:
       a primary (Primary/is_primary) element found at level 2 forces at
       least "ชำรุด", level 1 forces at least "วิกฤติ", level 0 forces
       "วิบัติ" - whichever of (band status, forced status) is worse wins.
       Non-primary elements (railing, joints, wearing surface, ...) never
       trigger this rule, only load-bearing elements do (columns, beams,
       decks, pier caps, abutments, foundations).
"""

import sys
from dataclasses import dataclass

if sys.stdout.encoding is not None and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# 4.4 - C_hi: condition level (0-5) -> health coefficient
# ---------------------------------------------------------------------------
C_HI = {
    5: 1.00,
    4: 0.83,
    3: 0.67,
    2: 0.33,
    1: 0.17,
    0: 0.00,
}


# ---------------------------------------------------------------------------
# 4.6 - Element and T-BHI formulas
# ---------------------------------------------------------------------------
@dataclass
class Element:
    """
    One structural element inspected by drone.

    name:        display name, e.g. "เสาตอม่อ"
    q:           quantity of the element (area or count), used as the T-BHI weight
    W:           importance weight of this element (from the project's table 4.5)
    is_primary:  True for load-bearing / principal elements whose condition can
                 trigger the 4.8 mandatory rule - columns, beams/girders, deck,
                 pier caps, abutments, foundations/piles.
                 False for non-structural elements that never trigger it -
                 railings, joints, wearing surface, coatings, etc.
    proportions: fraction of this element's area at each condition level 0-5,
                 e.g. {5: 0.75, 3: 0.15, 2: 0.10}. Must sum to 1.0. Levels with
                 zero area may be omitted.
    """
    name: str
    q: float
    W: float
    is_primary: bool
    proportions: dict[int, float]

    def __post_init__(self) -> None:
        if not self.proportions:
            raise ValueError(f"{self.name!r}: proportions must not be empty")
        for level in self.proportions:
            if level not in C_HI:
                raise ValueError(f"{self.name!r}: invalid level {level}, must be 0-5")
        total = sum(self.proportions.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"{self.name!r}: proportions must sum to 1.0, got {total}")

    @property
    def ehi(self) -> float:
        """4.6 step 1: EHI = sum(C_hi * proportion) * 100"""
        return sum(C_HI[level] * frac for level, frac in self.proportions.items()) * 100

    @property
    def levels_present(self) -> set[int]:
        """Condition levels that actually have nonzero area on this element."""
        return {level for level, frac in self.proportions.items() if frac > 0}


def compute_tbhi(elements: list[Element]) -> float:
    """4.6 step 2: T-BHI = sum(q * W * EHI) / sum(q * W)"""
    numerator = sum(e.q * e.W * e.ehi for e in elements)
    denominator = sum(e.q * e.W for e in elements)
    if denominator <= 0:
        raise ValueError("sum(q * W) must be > 0")
    return numerator / denominator


def calculate_tbhi(elements: list[Element]) -> tuple[float, str]:
    """
    Full 4.6 + 4.8 pipeline for one bridge.

    Every number that feeds the result (q, W, EHI, proportions) comes only
    from `elements` - nothing about a specific bridge is hardcoded here, so
    this same function works for any bridge passed in.
    """
    tbhi = compute_tbhi(elements)
    status = classify(elements, tbhi)
    return tbhi, status


# ---------------------------------------------------------------------------
# 4.8 - Status bands and the mandatory (primary-element) rule
# ---------------------------------------------------------------------------
# Worst-to-best is last-to-first in this list; order matters for "take the worse".
STATUS_BANDS = [
    (100, 101, "ดีมาก"),      # = 100
    (90, 100, "ดีพอใช้"),     # 90 <= T-BHI < 100
    (70, 90, "พอใช้"),        # 70 <= T-BHI < 90
    (50, 70, "ชำรุด"),        # 50 <= T-BHI < 70
    (30, 50, "วิกฤติ"),       # 30 <= T-BHI < 50
    (0, 30, "วิบัติ"),        # T-BHI < 30
]
STATUS_ORDER = [label for _, _, label in STATUS_BANDS]  # best -> worst

# A primary element found at this level forces at least this status.
# Levels 3, 4, 5 never force anything.
FORCED_FLOOR_BY_LEVEL = {
    2: "ชำรุด",
    1: "วิกฤติ",
    0: "วิบัติ",
}


def band_status(tbhi: float) -> str:
    """4.8 table: plain T-BHI -> status, before the mandatory rule."""
    for lo, hi, label in STATUS_BANDS:
        if lo <= tbhi < hi:
            return label
    return STATUS_BANDS[-1][2]


def worst_primary_level(elements: list[Element]) -> int | None:
    """Lowest condition level found with nonzero area on any primary element."""
    levels = {lvl for e in elements if e.is_primary for lvl in e.levels_present}
    return min(levels) if levels else None


def mandatory_floor(elements: list[Element]) -> str | None:
    """4.8 mandatory rule: forced minimum status from primary elements, or None."""
    level = worst_primary_level(elements)
    if level is None:
        return None
    return FORCED_FLOOR_BY_LEVEL.get(level)


def classify(elements: list[Element], tbhi: float) -> str:
    """
    Full 4.8 classification: compute the band status from T-BHI, then apply
    the mandatory primary-element rule, taking whichever status is worse.
    """
    status = band_status(tbhi)
    floor = mandatory_floor(elements)
    if floor is not None:
        status_rank = STATUS_ORDER.index(status)
        floor_rank = STATUS_ORDER.index(floor)
        if floor_rank > status_rank:  # higher index = worse
            status = floor
    return status


def _report(elements: list[Element], title: str) -> tuple[float, str]:
    print(f"\n=== {title} ===")
    print(f"{'ชิ้นส่วน':<16}{'q':>8}{'W':>5}{'primary':>9}{'EHI':>10}")
    for e in elements:
        print(f"{e.name:<16}{e.q:>8}{e.W:>5}{str(e.is_primary):>9}{e.ehi:>10.2f}")

    tbhi, final_status = calculate_tbhi(elements)
    band = band_status(tbhi)
    floor = mandatory_floor(elements)

    print(f"\nT-BHI = {tbhi:.2f}")
    print(f"สถานะจากคะแนน (ก่อนกฎบังคับ) = {band}")
    print(f"กฎบังคับจากชิ้นส่วนหลัก (Primary) = {floor if floor else '(ไม่มี)'}")
    print(f"สถานะสุดท้าย = {final_status}")
    return tbhi, final_status


if __name__ == "__main__":
    # 4.7 worked example - used as the regression check. This data lives only
    # here, never inside calculate_tbhi() / compute_tbhi(), so those functions
    # stay generic and work for any bridge passed in.
    worked_example = [
        Element(
            name="เสาตอม่อ",
            q=40, W=10, is_primary=True,
            proportions={2: 4 / 40, 3: 6 / 40, 5: 30 / 40},
        ),
        Element(
            name="คานหลัก",
            q=60, W=10, is_primary=True,
            proportions={3: 3 / 60, 5: 57 / 60},
        ),
        Element(
            name="พื้นสะพาน",
            q=100, W=9, is_primary=True,
            proportions={5: 1.0},
        ),
        Element(
            name="คานรัดหัวเสา",
            q=20, W=9, is_primary=True,
            proportions={2: 1 / 20, 5: 19 / 20},
        ),
    ]

    tbhi, final_status = _report(worked_example, "ตัวอย่างส่วน 4.7")

    expected_tbhi = 96.99
    assert abs(tbhi - expected_tbhi) < 0.01, f"expected T-BHI {expected_tbhi}, got {tbhi:.2f}"

    expected_status = "ชำรุด"
    assert final_status == expected_status, (
        f"expected final status {expected_status!r} (mandatory rule from "
        f"เสาตอม่อ ระดับ 2, which is is_primary=True), got {final_status!r}"
    )

    print(
        f"\n[OK] T-BHI = {tbhi:.2f} (expected {expected_tbhi}) "
        f"and final status = {final_status!r} (expected {expected_status!r}), "
        f"not the naive band-only 'ดีพอใช้'."
    )

    # Second, independent bridge with completely different numbers, to prove
    # calculate_tbhi() is driven purely by its `elements` argument and not by
    # anything baked in from the 4.7 example above.
    second_bridge = [
        Element(
            name="เสาตอม่อ",
            q=25, W=8, is_primary=True,
            proportions={1: 0.10, 4: 0.30, 5: 0.60},
        ),
        Element(
            name="คานหลัก",
            q=50, W=7, is_primary=True,
            proportions={4: 0.20, 5: 0.80},
        ),
        Element(
            name="ราวสะพาน",
            q=12, W=2, is_primary=False,
            proportions={2: 0.50, 5: 0.50},
        ),
    ]

    tbhi2, final_status2 = _report(second_bridge, "สะพานทดสอบตัวที่ 2")

    assert abs(tbhi2 - expected_tbhi) > 0.01, (
        f"สะพานทดสอบตัวที่ 2 ควรได้ T-BHI ต่างจาก {expected_tbhi} แต่ได้ {tbhi2:.2f} ซ้ำกัน"
    )

    print(
        f"\n[OK] สะพานทดสอบตัวที่ 2: T-BHI = {tbhi2:.2f}, สถานะ = {final_status2!r} "
        f"- คนละค่ากับตัวอย่าง 4.7 ({expected_tbhi}) พิสูจน์ว่า calculate_tbhi() "
        f"รับค่าจาก elements จริง ไม่ได้ฝังค่าไว้ในตัวคำนวณ"
    )
