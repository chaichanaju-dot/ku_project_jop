"""
Element weight (W) and primary/secondary lookup for T-BHI.

Source: "คู่มือเริ่มต้นโปรเจกต์ประเมินสะพานจากภาพโดรน"
  - section 4.5 (ตารางถ่วงน้ำหนักชิ้นส่วน, from Pellegrino) -> ELEMENT_WEIGHT
  - section 2.1 (Primary element = ชิ้นส่วนที่พังแล้วสะพานรับน้ำหนักไม่ได้:
    คานหลัก เสาตอม่อ พื้นสะพาน คานรัดหัวเสา ตอม่อริมตลิ่ง ฐานราก) -> ELEMENT_IS_PRIMARY

Only the 4 element classes this project's YOLO model labels (see section 8.1)
are covered here: pier, girder, pier_cap, deck.
"""

# 4.5: Columns=10, Girders/Beams=10, Pier Caps=9, Decks=9
ELEMENT_WEIGHT = {
    "pier": 10,
    "girder": 10,
    "pier_cap": 9,
    "deck": 9,
}

# 2.1: all four are load-bearing elements whose failure means the bridge
# can't carry load, so all are primary.
ELEMENT_IS_PRIMARY = {
    "pier": True,
    "girder": True,
    "pier_cap": True,
    "deck": True,
}


if __name__ == "__main__":
    assert set(ELEMENT_WEIGHT) == set(ELEMENT_IS_PRIMARY) == {"pier", "girder", "pier_cap", "deck"}
    assert ELEMENT_WEIGHT["pier"] == 10 and ELEMENT_IS_PRIMARY["pier"] is True
    assert ELEMENT_WEIGHT["girder"] == 10 and ELEMENT_IS_PRIMARY["girder"] is True
    assert ELEMENT_WEIGHT["pier_cap"] == 9 and ELEMENT_IS_PRIMARY["pier_cap"] is True
    assert ELEMENT_WEIGHT["deck"] == 9 and ELEMENT_IS_PRIMARY["deck"] is True
    print("[OK] element_lookup matches section 4.5 (W) and 2.1 (primary) of the guide")
