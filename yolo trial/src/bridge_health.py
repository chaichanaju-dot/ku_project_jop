# T-BHI (Thai Bridge Health Index) calculator - sections 4.4/4.6/4.7/4.8 of
# "คู่มือเริ่มต้นโปรเจกต์ประเมินสะพานจากภาพโดรน":
#   EHI   = sum(C_hi * proportion_of_area) * 100         (per element)
#   T-BHI = sum(q * W * EHI) / sum(q * W)                (whole bridge)
#   then the mandatory rule (4.8): a primary element found at level 2/1/0
#   forces the final status to at least ชำรุด/วิกฤติ/วิบัติ, whichever is worse.

import sys
from dataclasses import dataclass

if sys.stdout.encoding is not None and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

C_HI = {5: 1.00, 4: 0.83, 3: 0.67, 2: 0.33, 1: 0.17, 0: 0.00}


@dataclass
class Element:
    name: str
    q: float
    W: float
    is_primary: bool
    proportions: dict[int, float]  # condition level 0-5 -> fraction of area, must sum to 1.0

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
        return sum(C_HI[level] * frac for level, frac in self.proportions.items()) * 100

    @property
    def levels_present(self) -> set[int]:
        return {level for level, frac in self.proportions.items() if frac > 0}


def compute_tbhi(elements: list[Element]) -> float:
    numerator = sum(e.q * e.W * e.ehi for e in elements)
    denominator = sum(e.q * e.W for e in elements)
    if denominator <= 0:
        raise ValueError("sum(q * W) must be > 0")
    return numerator / denominator


def calculate_tbhi(elements: list[Element]) -> tuple[float, str]:
    tbhi = compute_tbhi(elements)
    return tbhi, classify(elements, tbhi)


STATUS_BANDS = [
    (100, 101, "ดีมาก"),
    (90, 100, "ดีพอใช้"),
    (70, 90, "พอใช้"),
    (50, 70, "ชำรุด"),
    (30, 50, "วิกฤติ"),
    (0, 30, "วิบัติ"),
]
STATUS_ORDER = [label for _, _, label in STATUS_BANDS]  # best -> worst

FORCED_FLOOR_BY_LEVEL = {2: "ชำรุด", 1: "วิกฤติ", 0: "วิบัติ"}


def band_status(tbhi: float) -> str:
    for lo, hi, label in STATUS_BANDS:
        if lo <= tbhi < hi:
            return label
    return STATUS_BANDS[-1][2]


def worst_primary_level(elements: list[Element]) -> int | None:
    levels = {lvl for e in elements if e.is_primary for lvl in e.levels_present}
    return min(levels) if levels else None


def mandatory_floor(elements: list[Element]) -> str | None:
    level = worst_primary_level(elements)
    return None if level is None else FORCED_FLOOR_BY_LEVEL.get(level)


def classify(elements: list[Element], tbhi: float) -> str:
    status = band_status(tbhi)
    floor = mandatory_floor(elements)
    if floor is not None and STATUS_ORDER.index(floor) > STATUS_ORDER.index(status):
        status = floor
    return status


def _report(elements: list[Element], title: str) -> tuple[float, str]:
    print(f"\n=== {title} ===")
    print(f"{'ชิ้นส่วน':<16}{'q':>8}{'W':>5}{'primary':>9}{'EHI':>10}")
    for e in elements:
        print(f"{e.name:<16}{e.q:>8}{e.W:>5}{str(e.is_primary):>9}{e.ehi:>10.2f}")

    tbhi, final_status = calculate_tbhi(elements)
    print(f"\nT-BHI = {tbhi:.2f}")
    print(f"สถานะจากคะแนน (ก่อนกฎบังคับ) = {band_status(tbhi)}")
    print(f"กฎบังคับจากชิ้นส่วนหลัก (Primary) = {mandatory_floor(elements) or '(ไม่มี)'}")
    print(f"สถานะสุดท้าย = {final_status}")
    return tbhi, final_status


if __name__ == "__main__":
    worked_example = [
        Element(name="เสาตอม่อ", q=40, W=10, is_primary=True, proportions={2: 4 / 40, 3: 6 / 40, 5: 30 / 40}),
        Element(name="คานหลัก", q=60, W=10, is_primary=True, proportions={3: 3 / 60, 5: 57 / 60}),
        Element(name="พื้นสะพาน", q=100, W=9, is_primary=True, proportions={5: 1.0}),
        Element(name="คานรัดหัวเสา", q=20, W=9, is_primary=True, proportions={2: 1 / 20, 5: 19 / 20}),
    ]

    tbhi, final_status = _report(worked_example, "ตัวอย่างส่วน 4.7")
    assert abs(tbhi - 96.99) < 0.01, f"expected T-BHI 96.99, got {tbhi:.2f}"
    assert final_status == "ชำรุด", f"expected ชำรุด (forced by เสาตอม่อ level 2), got {final_status!r}"
    print(f"\n[OK] T-BHI = {tbhi:.2f}, สถานะ = {final_status!r} (mandatory rule applied, not naive 'ดีพอใช้')")

    second_bridge = [
        Element(name="เสาตอม่อ", q=25, W=8, is_primary=True, proportions={1: 0.10, 4: 0.30, 5: 0.60}),
        Element(name="คานหลัก", q=50, W=7, is_primary=True, proportions={4: 0.20, 5: 0.80}),
        Element(name="ราวสะพาน", q=12, W=2, is_primary=False, proportions={2: 0.50, 5: 0.50}),
    ]

    tbhi2, final_status2 = _report(second_bridge, "สะพานทดสอบตัวที่ 2")
    assert abs(tbhi2 - 96.99) > 0.01, "สะพานทดสอบตัวที่ 2 ควรได้ T-BHI ต่างจากตัวอย่าง 4.7"
    print(f"\n[OK] สะพานทดสอบตัวที่ 2: T-BHI = {tbhi2:.2f}, สถานะ = {final_status2!r} - คนละค่ากับตัวอย่าง 4.7")
