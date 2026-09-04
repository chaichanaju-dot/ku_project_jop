# W and is_primary per "คู่มือเริ่มต้นโปรเจกต์ประเมินสะพานจากภาพโดรน" section 4.5 (weights) and 2.1 (primary elements)

ELEMENT_WEIGHT = {"pier": 10, "girder": 10, "pier_cap": 9, "deck": 9}
ELEMENT_IS_PRIMARY = {"pier": True, "girder": True, "pier_cap": True, "deck": True}


if __name__ == "__main__":
    assert set(ELEMENT_WEIGHT) == set(ELEMENT_IS_PRIMARY) == {"pier", "girder", "pier_cap", "deck"}
    assert ELEMENT_WEIGHT["pier"] == 10 and ELEMENT_WEIGHT["pier_cap"] == 9
    assert all(ELEMENT_IS_PRIMARY.values())
    print("[OK] element_lookup")
