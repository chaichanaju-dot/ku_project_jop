# ทดสอบสูตร: หาระยะห่างจริงระหว่าง 2 จุดในภาพเดียวกัน จาก pixel + สเปกกล้อง + มุมกิมบอล + ระยะแนวราบ
# แก้จากรุ่นแรก: จุด A กับ B อาจอยู่คนละความสูง/ความลึกจากกล้อง ไม่ใช่ระนาบเดียวกัน
# เลยต้องคำนวณ "ระยะตามแนวลำแสง" ของแต่ละจุดแยกกัน โดยใช้ระยะแนวราบ (จาก GPS, เชื่อถือได้) ตรึงไว้
# แล้วปรับตามมุมเงย/ก้มจริงของแต่ละ pixel (ไม่ใช่ใช้ระยะเดียวกันทั้งภาพเหมือนรุ่นแรกที่ผิด)
import math

# ---- แก้ค่าตรงนี้ตามภาพจริงที่จะทดสอบ ----
IMG_W = 5280                  # ความกว้างภาพ (pixel)
IMG_H = 3956                  # ความสูงภาพ (pixel)
FOCAL_35MM = 24.0             # Focal Length 35mm equivalent (mm)
GIMBAL_PITCH_DEG = 3.70       # มุมเงย/ก้มกล้องจริงจาก EXIF (0 = แนวนอน, บวก = เงยขึ้น)
HORIZONTAL_DISTANCE_MM = 7440 # ระยะแนวราบจากกล้องถึงบริเวณจุด (จาก GPS lat/lon กล้อง<->จุด, เชื่อถือได้กว่า altitude)
POINT_A = (2000, 1800)        # (px, py) จุด A
POINT_B = (2400, 1750)        # (px, py) จุด B


def fov_from_focal_35mm(focal_35mm):
    return 2 * math.atan(36 / (2 * focal_35mm))


def pixel_to_point_3d(px, py, img_w, img_h, fov_h, gimbal_pitch_rad, horizontal_mm):
    # หามุมเบี่ยงของ pixel นี้จากกึ่งกลางภาพ (เหมือนเดิม)
    fov_v = fov_h * img_h / img_w
    offset_x = (px - img_w / 2) / (img_w / 2)
    offset_y = (py - img_h / 2) / (img_h / 2)
    angle_x = math.atan(offset_x * math.tan(fov_h / 2))       # มุมเบี่ยงแนวนอนของ pixel นี้
    angle_y = math.atan(offset_y * math.tan(fov_v / 2))       # มุมเบี่ยงแนวตั้งของ pixel นี้

    # จุดสำคัญที่แก้ต่างจากเดิม: มุมเงย/ก้มจริงของ "ลำแสง" ที่ไปถึง pixel นี้ = มุมกิมบอล + มุมเบี่ยงของ pixel
    total_vertical_angle = gimbal_pitch_rad + angle_y
    # ระยะตามแนวลำแสง (ต้องยาวกว่าระยะแนวราบ ถ้าลำแสงเงย/ก้มมาก) หาได้จาก ระยะแนวราบ / cos(มุมรวม)
    ray_distance_mm = horizontal_mm / math.cos(total_vertical_angle)

    # ตำแหน่งจริง (x,y,z) ของจุดนี้ เทียบจุดกึ่งกลางที่กล้องมองตรง โดยใช้ระยะเฉพาะจุดนี้ (ไม่ใช้ค่าเดียวกันทั้งภาพ)
    x_mm = ray_distance_mm * math.tan(angle_x)                # ตำแหน่งแนวนอน
    z_mm = ray_distance_mm * math.sin(total_vertical_angle)   # ความสูงจริงเทียบกล้อง (แกนตั้ง)
    y_mm = ray_distance_mm * math.cos(total_vertical_angle)   # ระยะลึกจริงจากกล้อง (แกนหน้า-หลัง)
    return x_mm, y_mm, z_mm


fov_h = fov_from_focal_35mm(FOCAL_35MM)
pitch_rad = math.radians(GIMBAL_PITCH_DEG)

ax, ay, az = pixel_to_point_3d(*POINT_A, IMG_W, IMG_H, fov_h, pitch_rad, HORIZONTAL_DISTANCE_MM)
bx, by, bz = pixel_to_point_3d(*POINT_B, IMG_W, IMG_H, fov_h, pitch_rad, HORIZONTAL_DISTANCE_MM)

# ระยะห่างจริงแบบ 3 มิติเต็มรูปแบบ (พีทาโกรัส 3 มิติ) ไม่ใช่แค่ 2 มิติเหมือนรุ่นแรก
distance_mm = math.sqrt((bx-ax)**2 + (by-ay)**2 + (bz-az)**2)

print(f"จุด A (x,y,z): ({ax:.1f}, {ay:.1f}, {az:.1f}) mm")
print(f"จุด B (x,y,z): ({bx:.1f}, {by:.1f}, {bz:.1f}) mm")
print(f"ระยะห่างที่คำนวณได้จากภาพ (3 มิติเต็ม): {distance_mm:.1f} mm ({distance_mm/10:.2f} cm)")
print("เอาไปเทียบกับระยะจริงที่วัดจากโมเดล 3D แล้วดูว่าคลาดเคลื่อนกี่ %")
