# คำนวณระยะห่างจริง (เมตร) ระหว่าง 2 พิกัด GPS (lat, lon, ความสูง) - ใช้ระบบ WGS84 เดียวกับที่ NP Survey โชว์
# ใช้ได้ทั้ง: (1) หาระยะจริงระหว่างจุด A-B จากโมเดล 3D (ground truth เทียบกับค่าที่คำนวณจากภาพ)
#           (2) หาระยะห่างจากกล้อง (GPS จาก EXIF ภาพ) ถึงจุดบนโครงสร้าง (แทนการเดา DISTANCE_MM)
import math

EARTH_RADIUS_M = 6371000   # รัศมีโลกเฉลี่ย (เมตร) ใช้ในสูตร Haversine


def gps_distance_m(lat1, lon1, alt1, lat2, lon2, alt2):
    # Haversine formula หาระยะทางแนวราบ (ผิวโค้งโลก) ระหว่าง 2 จุด lat/lon ก่อน
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon/2)**2
    horizontal_m = 2 * EARTH_RADIUS_M * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # รวมผลต่างความสูงเข้าไปด้วย (พีทาโกรัสอีกชั้น เพราะแนวราบกับแนวดิ่งตั้งฉากกัน)
    vertical_m = alt2 - alt1
    distance_3d_m = math.hypot(horizontal_m, vertical_m)
    return distance_3d_m


# ---- ตัวอย่าง: แก้เป็นพิกัดจริงที่คลิกได้จาก NP Survey ----
POINT_A = (13.6866, 101.0779, 5.6336)   # (lat, lon, alt) จุด A บนโมเดล 3D
POINT_B = (13.6867, 101.0780, 5.7000)   # (lat, lon, alt) จุด B บนโมเดล 3D - ตัวอย่างสมมติ แก้เป็นค่าจริง

distance = gps_distance_m(*POINT_A, *POINT_B)
print(f"ระยะห่างจริงระหว่างจุด A-B (จากพิกัด GPS โมเดล 3D) = {distance:.3f} เมตร")
print("เอาไปเทียบกับระยะที่คำนวณได้จาก test_pixel_to_mm.py")
