# ลง software แยกลงโดรน DJI ได้ไหม — สรุปสถานะ DJI SDK ทั้งตระกูล (ส.ค. 2026) และแนวทางบินตรวจสอบสะพาน/เสาตอม่อ

# ลง software แยกลงโดรน DJI ได้ไหม — สรุปเชิงเทคนิค ส.ค. 2026

**คำตอบสั้น ๆ ก่อน:** ได้ แต่ "ลง software ลงโดรน" ในความหมายที่คนมักเข้าใจ (flash firmware ตัวเอง / เขียนโค้ดรันบน flight controller) **ทำไม่ได้เลย** DJI ให้คุณเขียนโปรแกรม 2 ที่เท่านั้น คือ (1) บน **Android app** ที่คุยกับ remote controller ผ่าน MSDK V5 และ (2) บน **คอมพิวเตอร์ที่คุณแขวนไว้กับตัวโดรน** (payload) ผ่าน PSDK V3 ตัว flight controller เป็นกล่องดำปิดสนิท

ด้านล่างคือรายละเอียดต่อหัวข้อตามที่ขอ พร้อมส่วนที่ 7 ตอบโจทย์เฉพาะหน้าเรื่องบินใกล้/วัดระยะ/stitching

---

## 1. Mobile SDK V5 (MSDK)

### 1.1 เวอร์ชันและ platform

| หัวข้อ | ค่า | หมายเหตุ |
|---|---|---|
| เวอร์ชันล่าสุด | **5.18.0** | จาก README ของ repo และ Maven Central artifact `com.dji:dji-sdk-v5-aircraft` |
| วันที่ release notes | เอกสาร "Android MSDK 5.18.0 Version Release Notes" เผยแพร่ **22 พ.ค. 2026** | ยืนยันได้จาก search index ของ developer.dji.com — ตัววันที่ commit จริงยังไม่ยืนยัน |
| Platform | **Android เท่านั้น** | ไม่มี MSDK V5 บน iOS และจะไม่มี |
| iOS | **ตาย** — DJI ประกาศหยุดอัปเดต iOS Mobile SDK มีผล **29 พ.ย. 2023** และเลิกรับ MFi application ใหม่ | เวอร์ชันสุดท้ายฝั่ง iOS คือสาย MSDK V4 (4.16.x) — ไม่มีสัญญาณว่าจะกลับมาในปี 2026 |

AAR ที่ต้องใส่มี 3 ตัว: `dji-sdk-v5-aircraft` (ตัวหลัก), `dji-sdk-v5-aircraft-provided` (interface สำหรับ compile), `dji-sdk-v5-networkImp` (network layer — ใส่โดย default ถ้าต้องใช้ฟังก์ชันที่ต่อเน็ต)

> **หมายเหตุความไม่แน่นอน:** `minSdkVersion` / JDK ที่ต้องใช้ **ยังไม่ยืนยัน** — README ที่ดึงมาไม่ระบุ ต้องไปดู `build.gradle` ใน `SampleCode-V5/android-sdk-v5-sample/` ของ repo โดยตรง

### 1.2 รุ่นอากาศยานที่รองรับ (จาก README เวอร์ชัน 5.18.0)

**Enterprise:** Matrice 400, Matrice 4D Enterprise Series (M4D/M4TD), Matrice 4 Enterprise Series (M4E/M4T), Matrice 350 RTK, Matrice 300 RTK, M30 Series (M30/M30T), Mavic 3 Enterprise Series (M3E/M3T/M3M), Mavic 3TA
**Consumer:** DJI Mini 4 Pro, DJI Mini 3 Pro, DJI Mini 3
**Payload:** H30 Series

**สิ่งที่ต้องรู้:** ฝั่ง consumer รองรับแค่ Mini 3 / Mini 3 Pro / Mini 4 Pro เท่านั้น — **Air series และ Mavic 3 ตัว consumer ไม่อยู่ในลิสต์** และแม้แต่รุ่นที่อยู่ในลิสต์ก็ไม่ได้รองรับทุก API เช่น Mini 3 / Mini 3 Pro **ไม่รองรับ obstacle avoidance แบบ BRAKE** จึงเปิด/ปิด sub-switch ของ obstacle avoidance ไม่ได้ นี่คือกับดักที่คนซื้อ Mini มาแล้วเขียนโค้ดไม่ได้ตามคาดบ่อยที่สุด

### 1.3 โมดูลทั้งหมด (อ้างจากรายชื่อ Fragment ใน sample app จริง)

รายชื่อไฟล์ใน `SampleCode-V5/.../pages/` คือคำตอบที่ตรงที่สุดว่า MSDK V5 ทำอะไรได้บ้าง:

| กลุ่ม | Fragment / Manager | ทำอะไร |
|---|---|---|
| Waypoint | `WayPointV3Fragment` — `IWaypointMissionManager`, `IWPMZManager` | บิน mission แบบ KMZ/WPML |
| Manual control | `VirtualStickFragment` — `IVirtualStickManager` | ส่ง stick command จากโค้ด |
| Perception | `PerceptionFragment` — `IPerceptionManager` | อ่านระยะสิ่งกีดขวาง, ตั้งระยะเตือน/เบรก |
| RTK | `RTKCenterFragment`, `RTKNetworkFragment`, `RTKStationFragment` | Network RTK / D-RTK base station |
| Media | `MediaFragment`, `MediaFileDetailsFragment`, `LocalFileFragment` | list/download ไฟล์จากอากาศยาน |
| Streaming | `LiveFragment`, `VideoChannelFragment`, `MultiVideoChannelFragment`, `CameraStreamListFragment`, `CameraStreamDetailFragment`, `VideoPlayFragment` | live stream ออก + ดึง decoded frame |
| Simulator | `SimulatorFragment` — `ISimulatorManager` | บินจำลองไม่ต้องขึ้นจริง |
| Camera/Gimbal/ทุกอย่าง | `KeyValueFragment` — **KeyManager** | API หลักของ V5 ทั้งหมด (get/set/listen/action ผ่าน Key) |
| Payload (PSDK) | `PayloadCenterFragment`, `PayLoadDataFragment`, `PayloadWidgetFragment` | คุยกับ payload ที่เขียนด้วย PSDK |
| MOP | `MOPCenterFragment`, `MopInterfaceFragment`, `MopDownFragment` | ช่องส่งข้อมูลตรงระหว่าง app ↔ payload |
| AI/Intelligent | `IntelligentFlightFragment`, `LookAtFragment`, `IntelligentBoxFragment` | tracking / POI / AI detection box |
| อื่น ๆ | `FlySafeFragment`, `LTEFragment`, `MegaphoneFragment`, `TTSFragment`, `UpgradeFragment`, `DiagnosticFragment`, `FlightRecordFragment`, `UAS*Fragment` (Remote ID จีน/EU/ฝรั่งเศส/ญี่ปุ่น/US) | GEO zone info, 4G เสริมสัญญาณ, ลำโพง, อัปเฟิร์มแวร์, Remote ID |

**ข้อสังเกตสำคัญ:** V5 เปลี่ยนสถาปัตยกรรมจาก V4 อย่างสิ้นเชิง — V4 ใช้ object แยกต่อ component (`DJICamera`, `DJIGimbal`) แต่ V5 รวมเกือบทุกอย่างไว้ใน **KeyManager** (`KeyTools.createKey(CameraKey.KeyShootPhoto)` แล้ว `performAction`/`getValue`/`listen`) โค้ดตัวอย่างจาก V4 ที่หาเจอตามเน็ตส่วนใหญ่**ใช้กับ V5 ไม่ได้** นี่เป็นสาเหตุอันดับหนึ่งของความสับสน

### 1.4 Waypoint Mission — WPML/KMZ

**`IWaypointMissionManager`** (ยืนยันจาก API reference):
- `pushKMZFileToAircraft(String missionFilePath, CompletionCallbackWithProgress<Double> callback)` — อัปโหลดไฟล์เข้า flight controller
- `startMission(String missionFileName, CompletionCallback)` — บินทั้ง mission
- `startMission(String missionFileName, List<Integer> waylineIDs, CompletionCallback)` — เลือกเฉพาะบาง wayline
- `startMission(String missionFileName, BreakPointInfo, CompletionCallback)` — บินต่อจากจุดที่ค้าง
- `pauseMission` / `resumeMission` (2 overload) / `stopMission(String missionFileName, ...)`
- `queryBreakPointInfoFromAircraft(String missionFileName, CompletionCallbackWithParam<BreakPointInfo>)`
- Listener: `WaypointMissionExecuteStateListener`, `WaylineExecutingInfoListener`, `WaypointActionListener`

**ข้อจำกัดที่ระบุในเอกสารตรง ๆ:**
- **M300 RTK และ M350 RTK รองรับได้แค่ 1 wayline ID** เท่านั้น
- M300/M350 RTK **ใช้ `queryBreakPointInfoFromAircraft` ไม่ได้**
- ห้ามเรียก `KeyStartGoHome` ระหว่างช่วง takeoff ของ mission

**`IWPMZManager`** ทำหน้าที่ edit/import/export/ตรวจ KMZ ก่อนอัปโหลด — `generateKMZFile()` สร้างไฟล์จาก template object, `checkValidation()` ตรวจ static field ก่อน push

**โครงสร้างไฟล์:** KMZ คือ zip ที่ข้างในต้องมี `template.kml` และ **`waylines.wpml`** — ชื่อไฟล์ zip ตั้งเองได้ แต่ชื่อโฟลเดอร์/ไฟล์ข้างในเปลี่ยนไม่ได้ **firmware จะ execute `waylines.wpml`** ไม่ใช่ `template.kml` (ถ้าคุณ generate มาแต่ `template.kml` mission จะไม่วิ่ง — เป็นบั๊กยอดฮิต)

### 1.5 Virtual Stick

`IVirtualStickManager`: `enableVirtualStick` / `disableVirtualStick` / `getLeftStick` / `getRightStick` / `setVirtualStickAdvancedModeEnabled(boolean)` / `sendVirtualStickAdvancedParam(VirtualStickFlightControlParam)` / listener

| ข้อจำกัด | ค่าจริง |
|---|---|
| ความถี่ที่ควรส่ง | **5–25 Hz** |
| obstacle avoidance ใน advanced mode | ทำงานเฉพาะเมื่อ vertical = **velocity mode**, yaw = **angular velocity mode**, roll/pitch = **velocity mode** เท่านั้น |
| รุ่นที่รองรับ OA ตอนใช้ virtual stick | **M300 RTK, M350 RTK, M30 series, Mavic 3E series, Mavic 3M** เท่านั้น |
| firmware | ต่ำกว่า **V7.01.10.03** → obstacle sensing ถูกปิด |
| เขต restricted | เข้าใกล้ประมาณ **30 m** → **RC ยึดการควบคุมคืน** virtual stick ใช้ไม่ได้ทันที |
| ข้อดี advanced mode | มี wind compensation ตอน hover เมื่อ GPS ดี |

### 1.6 Perception — ตัวที่ตอบโจทย์ "โดรนห่างวัตถุเท่าไหร่"

`IPerceptionManager`:
- `setObstacleAvoidanceType(BRAKE | BYPASS | CLOSE, callback)` — **`setOverallObstacleAvoidanceEnabled` ถูก deprecate ตั้งแต่ MSDK 5.1.0** ให้ใช้ตัวนี้แทน
- `setObstacleAvoidanceEnabled(...)` — sub-switch ราย `PerceptionDirection` (UPWARD / DOWNWARD / HORIZONTAL)
- `setObstacleAvoidanceWarningDistance(double, PerceptionDirection, callback)`
- `setObstacleAvoidanceBrakingDistance(double, PerceptionDirection, callback)`
- `setVisionPositioningEnabled(boolean)` — hover ตอน GPS อ่อน
- `setPrecisionLandingEnabled(boolean)` — ต้อง takeoff สูง ≥ **7 m**
- `addObstacleDataListener(ObstacleDataListener)` / `addPerceptionInformationListener(...)`

**ช่วงค่าที่ตั้งได้ (ตัวอย่าง M30 Series — เอกสารระบุตรง ๆ ว่าค่าต่างกันตามรุ่น):**

| พารามิเตอร์ | ช่วง |
|---|---|
| Horizontal warning distance | **[1.1, 33.0] m** |
| Downward warning distance | **[0.6, 33.0] m** |
| Horizontal braking distance | **[1.0, 10.0] m** |
| Downward braking distance | **[0.5, 3.0] m** |

**`ObstacleData` (นี่คือของจริงที่ใช้วัดระยะ):**
- `getHorizontalObstacleDistance()` — array, **หน่วย millimeter**
- `getHorizontalAngleInterval()` — ระยะห่างเชิงมุมต่อ index (ตามฟอรัม DJI คือช่องละ **1 องศา**, index 0 = ทิศหัวเครื่อง, 90 = ขวา, 180 = ท้าย)
- `getUpwardObstacleDistance()` / `getDownwardObstacleDistance()` — mm เช่นกัน
- ค่า **60000** = ไม่พบสิ่งกีดขวาง (ระบุในฟอรัม DJI SDK; API reference หน้าที่ดึงมาไม่ได้ระบุ sentinel นี้ → **confidence กลาง**)

### 1.7 Camera / Gimbal / RTK / Media / LiveStream / Simulator

- **Camera/Gimbal**: ผ่าน KeyManager (`CameraKey.*`, `GimbalKey.*`) — ถ่ายภาพ, ตั้ง exposure, zoom, rotate gimbal (absolute/relative), thermal palette ฯลฯ  บั๊กที่พบจริงในปี 2026: issue **#609** `KeyCameraZoomRatiosRange` อ่านไม่ได้บน **H30T + Matrice 400 (MSDK 5.15)**
- **Laser Rangefinder (LRF)**: `KeyLaserWorkMode` = `OPEN_ON_DEMAND` → `KeyLaserMeasureEnabled` → listen `KeyLaserMeasureInformation` → อ่าน `targetDistance` (ดูข้อ 7)
- **RTK**: มี 3 หน้าใน sample — RTK Center, Network RTK, RTK Station (D-RTK base) PSDK 3.14.0 เพิ่ม **custom network RTK** ฝั่ง payload ด้วย  *(รายละเอียด interface `IRTKCenterManager` — หน้า API reference ที่เดาไว้ตอบ 404 → **ยังไม่ยืนยันชื่อคลาสที่แน่นอน** ต้องเปิดจาก `RTKCenterFragment.kt` ใน repo)*
- **Media**: list / download ไฟล์จาก SD card ของอากาศยาน — บั๊กที่รายงานจริงปี 2026: **#794 native crash ตอนดึง media**
- **LiveStream**: sample มี `LiveFragment` — DJI รองรับ RTMP / RTSP / GB28181 / Agora *(ชื่อ protocol ทั้ง 4 มาจากความรู้ทั่วไปของ MSDK, **ยังไม่ได้ยืนยันจากหน้า API reference ในรอบนี้** เพราะ URL `ILiveStreamManager` ตอบ 404 — ให้ไปดู `LiveFragment.kt`)* บั๊กจริง: **#793 RTSP บน M300 ใช้ไม่ได้**, **#801 วิดีโอกระตุกบน M3T เมื่อ channel mode = automatic**
- **Simulator**: `ISimulatorManager` — `isSimulatorEnabled()`, `enableSimulator()`, `disableSimulator()`, listener ตั้งค่าผ่าน `InitializationSettings` *(พารามิเตอร์ lat/lon/จำนวนดาวเทียม — API reference ที่ดึงมาไม่ลงรายละเอียด, **ยังไม่ยืนยัน** ให้ดู `SimulatorFragment.kt`)*

### 1.8 ขั้นตอนขอ App Key / license

1. สมัคร developer account ที่ `developer.dji.com/register` — **ต้องใช้ email + บัตรเครดิตหรือเบอร์โทรเพื่อ verify** (บัตรไม่ถูกตัดเงิน)
2. เข้าแท็บ **Apps** → **Create App** → กรอก name, platform, **package identifier**, category, description
3. **package identifier ต้องตรงกับ `applicationId` ใน Gradle เป๊ะ ๆ** ผิดตัวเดียว register ไม่ผ่าน
4. DJI ส่ง activation email → กลับมาที่ dev center จะเห็น App Key
5. ใส่ใน `AndroidManifest.xml` เป็น meta-data `com.dji.sdk.API_KEY`
6. **MSDK ต้องต่อเน็ตเพื่อ verify App Key กับ server ของ DJI** — เครื่องที่ไม่มีเน็ตครั้งแรกจะ register ไม่ผ่าน (สำคัญมากสำหรับงานภาคสนามใต้สะพานในชนบท: ต้อง activate มาก่อนจากออฟฟิศ)

**สัญญา/กฎหมาย:** ใช้ภายใต้ DJI **END USER LICENSE AGREEMENT** (`developer.dji.com/policies/eula/`) ไม่มีค่าธรรมเนียมสำหรับการพัฒนา แต่มีข้อผูกพันเรื่องการไม่ reverse engineer, ไม่ bypass safety feature, และ DJI สงวนสิทธิ์เพิกถอน App Key ประเด็นสำคัญสำหรับงานวิจัย: **การเผยแพร่ app ที่ฝัง App Key ของคุณให้คนอื่นใช้ = คุณรับผิดชอบการใช้งานนั้น** สำหรับ project จบ ป.ตรี ที่ใช้ภายในทีมไม่มีปัญหา

### 1.9 ปัญหาที่ dev เจอบ่อยใน GitHub issues (ของจริง ปี 2026)

| Issue | วันที่ | ปัญหา |
|---|---|---|
| #805 | 28 ก.ค. 2026 | เลือก thermal-based detection ใน AI detection บน M4T ได้ไหม |
| #804 | 13 ก.ค. 2026 | ใช้ AI detection บน M400 ได้ไหม |
| #803 | 3 ก.ค. 2026 | mission file support ของ waypoint task ใน 5.18 |
| #802 | 30 มิ.ย. 2026 | Mavic 3 Enterprise ต่อแล้วหลุดวนลูป |
| #801 | 30 มิ.ย. 2026 | วิดีโอกระตุกบน M3T (channel mode = auto) |
| #799 | 29 มิ.ย. 2026 | `UnsatisfiedLinkError` กับ extension function ใน 5.18.0 |
| #798 | 20 มิ.ย. 2026 | app crash หลัง generate KMZ |
| #797 | 18 มิ.ย. 2026 | Mavic 3T take off ไม่ขึ้น |
| #796 | 17 มิ.ย. 2026 | `PayloadWidget.widgetName` โผล่เป็นภาษาจีน |
| #795 | 16 มิ.ย. 2026 | Mini 3 yaw เพี้ยนเมื่ออยู่ในร่ม |
| #794 | 10 มิ.ย. 2026 | native crash ตอนดึง media |
| #793 | 9 มิ.ย. 2026 | RTSP บน M300 พัง |
| #791 | — | Mini 4 Pro `startMission` ล้มเหลว `WPMZ_FILE_LOAD_ERROR` ทั้งที่ KMZ อัปโหลดสำเร็จ |
| #586 | — | `IWPMZManager.checkValidation` คืน `djiError={"value":[-10]}` โดยไม่บอกสาเหตุ |
| #618 | — | `PerceptionInfo` ไม่อัปเดตเมื่อเปลี่ยน `ObstacleAvoidanceType` |
| #402 | — | วิธี implement LRF ของ H20T |

**Pattern ที่เห็น:** ปัญหาแบ่งเป็น 3 กอง — (ก) รุ่นใหม่ (M400/M4T) รองรับไม่ครบ, (ข) KMZ/WPML สร้างแล้วโดนปฏิเสธโดยไม่บอกเหตุผลชัด, (ค) media/stream crash ระดับ native ซึ่ง debug เองไม่ได้เพราะเป็น `.so` ปิด

---

## 2. Payload SDK V3 (PSDK)

### 2.1 เวอร์ชันและ release history จริง

| เวอร์ชัน | วันที่ | สิ่งที่เพิ่ม |
|---|---|---|
| **3.16.0** | **1 เม.ย. 2026** | ติดตั้ง dependency บน Manifold 3 ได้โดยไม่ต้อง root; รองรับ USB WiFi ภายนอก (RTL8852BU, RTL88X2BU); **Attitude Mode control สำหรับ M4T/M4E**; อ่านเวลาบินคงเหลือ + battery threshold; camera status push |
| 3.15.0 | 11 ธ.ค. 2025 | Manifold 3 รองรับ M4E/M4T; Pilot version support M4D/4TD; แก้ streaming บน M400 |
| 3.14.1-fc100-fc30 | 25 พ.ย. 2025 | FlyCart 100 E-PORT Lite; UART baud auto-adapt; Hoist 2.0 |
| 3.14.0 | 4 พ.ย. 2025 | Zenmuse L3; **custom network RTK**; L2 บน M400 |
| 3.13.1 | 16 ก.ย. 2025 | Mavic 3TA; แก้ data subscription M300/M350; เปิด API ควบคุม RC-loss action |
| 3.12.0 | 27 มิ.ย. 2025 | **point cloud จาก LiDAR/mmWave radar**; **E-Port V2 (13.6 V / 17 V / 24 V)**; Manifold 3 AI app + AR drawing |

### 2.2 เปรียบเทียบ port ทั้ง 5 แบบ

| Port | อากาศยานที่ใช้ได้ | ไฟที่จ่าย | หน้าที่ |
|---|---|---|---|
| **SkyPort V2** | M300 RTK, M350 RTK (และสาย M200 V2 เดิม) | มี High Voltage mode | quick-release สำหรับ gimbal ที่ dev สร้างเอง, ต่อ flat-ribbon/coaxial |
| **SkyPort V3** | **Matrice 400 เท่านั้น — ใช้กับ M300/M350 ไม่ได้** | request ได้ **13.6 V / 17 V / 24 V** | quick-release gimbal + แปลง E-Port V2 เป็น coaxial link mode รองรับเฉพาะ **ONLY_USB_BULK** และ **ONLY_NETWORK** — **ไม่รองรับ** `UART_AND_NETWORK` / `UART_AND_USB_BULK` |
| **X-Port** | M300 / M350 / M400 | ผ่าน SkyPort | gimbal 3 แกนสำเร็จรูปจาก DJI — dev แค่ยัด sensor เข้าไป ไม่ต้องออกแบบ gimbal เอง |
| **E-Port** | Mavic 3E/3T, M30/M30T, M300 RTK, M350 RTK | **M3E/3T: 12–17.6 V/4 A · M30 series: 19.2–26.1 V/4 A · M300 RTK: 24 V/4 A · M350 RTK: 24 V/4 A** + XT30 12 V/2 A + XT30 5 V/2 A | แปลง E-Port เป็น XT30 + **USB 2.0** + UART/PPS บอร์ดขนาด **55×40×9 mm** |
| **E-Port V2** | **Matrice 400** (FlyCart 100 มี "E-PORT Lite") | **XT30 VCC: 13.8 V / 17.02 V / 24 V @ 5 A · XT30 12 V @ 4 A · XT30 5 V @ 4 A** | บอร์ด **89×60×13.4 mm** มี **onboard MCU** พร้อมพอร์ต General IO, UART, IIC/CAN, SPI, 5V/3.3V, UART Debug |
| **Extension Port** | M300 / M350 / M400 | — | ประสาน payload หลายตัวพร้อมกัน |

**คำเตือนจากคู่มือ E-Port V2 โดยตรง:** ถ้าใช้ XT30 ทั้ง 3 ช่องพร้อมกัน **กำลังไฟรวมต้องน้อยกว่ากำลังไฟสูงสุดต่อ 1 ช่องของอากาศยาน** — ห้ามคิดว่า 3 ช่อง = 3 เท่า

### 2.3 Bandwidth — **ยังไม่ยืนยัน**

ผมไม่พบตัวเลข Mbps ที่ยืนยันได้จากแหล่งทางการในรอบนี้ สิ่งที่ยืนยันได้คือ:
- E-Port มีพอร์ต **USB 2.0** (ทฤษฎี 480 Mbps แต่ throughput จริงของ PSDK ไม่ระบุ)
- E-Port V2 / SkyPort V3 รองรับ **link mode แบบ network** (Ethernet) และ **USB bulk**
- PSDK แยกช่องเป็น "low-speed" (custom data ระดับ KB) กับ "high-speed" (network) แต่ตัวเลขเพดานจริงไม่ประกาศ

**ต้องไปดูที่:** `developer.dji.com/doc/payload-sdk-tutorial/en/model-instruction/choose-hardware-platform.html` (หน้านี้ render ด้วย JS ดึงผ่าน HTTP ธรรมดาไม่ได้ ต้องเปิดในเบราว์เซอร์จริง) หรือถาม DJI SDK support โดยตรง **อย่าใช้ตัวเลขที่ผมเดา**

### 2.4 ภาษา / OS ฝั่ง payload

- **ภาษา: C** (SDK เป็น C library, ตัวอย่างมีทั้ง C และ C++ wrapper)
- **OS: Linux และ RTOS**
  - Linux: **ARM64, ARM32, x86_64** — build ด้วย CMake
  - RTOS: **ARM Cortex-M4 + FreeRTOS** (ตัวอย่างเป็น **STM32F4 Discovery**) — ต้อง implement **OSAL** (OS abstraction layer) และ **HAL** (hardware abstraction layer) เอง
- **ฮาร์ดแวร์ที่ DJI แนะนำ:** Manifold 3 (ปัจจุบัน, รองรับตั้งแต่ PSDK 3.15.0), เดิมคือ Manifold 2-C แต่ **ใช้ Raspberry Pi / Jetson ของตัวเองก็ได้** ถ้า toolchain ตรง (มี pre-compiled library หลาย toolchain ให้เลือก)
- **มาตรฐาน C ที่ต้องใช้ (C99/C11) — ยังไม่ยืนยัน** ต้องดู `CMakeLists.txt` ใน repo

### 2.5 Development Kit — ราคาและการเซ็นสัญญา

| Kit | SKU | ราคา | สถานะแหล่งข้อมูล |
|---|---|---|---|
| **E-Port Development Kit** | CP.EN.00000459.01 | **$133 USD** (Global Drone HQ, 2026) | ยืนยัน — ประกาศราคาสาธารณะ |
| **E-Port V2 Development Kit** | YCBZSS00321404 | **ยังไม่ยืนยัน** | มีขายจริง (DJI Store, Remote Robotic) แต่ไม่ประกาศราคาสาธารณะ |
| **SkyPort V2 Adapter Set** | — | **ยังไม่ยืนยัน** | ขายเป็นแพ็ก 10 ชิ้น หลายร้านบังคับ register ก่อนดูราคา ("manufacturer does not allow advertising the price online") |
| **X-Port** | — | **ยังไม่ยืนยัน** | อยู่ใน "Payload SDK Development Kit 2.0" |

**ในกล่อง E-Port V2 Development Kit** (จากคู่มือทางการ): E-Port V2 Development Board, **SkyPort V3 Adapter Ring**, **X-Port Adapter Board + X-Port Flat Ribbon Cable**, E-Port V2 Coaxial Cable (30 cm), SkyPort V3 Coaxial Cable (30 cm), Coaxial Cable Terminal (25 cm), XT30→USB-C Power Cable (20 cm), XT30→DC5.5 Power Cable

**Developer agreement:** repo PSDK มี `EULA.txt` — การพัฒนาและทดสอบใช้ได้ทันทีไม่ต้องเซ็นอะไรเพิ่ม แต่สำหรับการ **ผลิต payload เชิงพาณิชย์** DJI มีกระบวนการ partner/certification แยก **(รายละเอียดยังไม่ยืนยัน)** — ต้องติดต่อ DJI SDK support ถ้าจะทำเชิงพาณิชย์ สำหรับงานวิจัย/prototype ไม่ต้อง

---

## 3. Onboard SDK — ตายไปแล้วจริงไหม

**จริง ตายแล้ว**

| ข้อเท็จจริง | ค่า |
|---|---|
| เวอร์ชันสุดท้าย | **OSDK 4.1.0** |
| วันที่ release | **2 ก.พ. 2021** — 5 ปีครึ่งแล้ว ไม่มีอะไรใหม่เลย |
| ประกาศหยุดอัปเดตทางการ | **29 พ.ย. 2023** (ประกาศเดียวกับที่ฆ่า iOS MSDK และ Windows SDK) |
| ชะตากรรม | DJI **รวมฟังก์ชันของ OSDK เข้าไปใน PSDK** แล้ว |
| Technical support | ยังตอบคำถามอยู่ แต่ **ไม่ออกเวอร์ชันใหม่และไม่รับ MFi application ใหม่** |
| รุ่นที่ยังใช้ได้ | **M300 RTK** (ต้อง OSDK 4.0+), **M210 RTK V2**, **M210 V2** และรุ่นเก่ากว่า (M600/A3/N3) บน OSDK 3.x |

**คำแนะนำตรง ๆ:** ถ้าคุณกำลังจะเริ่มโปรเจกต์ใหม่ในปี 2026 **อย่าแตะ OSDK** ไม่มีรุ่นหลังปี 2021 รองรับ ไม่มีคนแก้บั๊ก README ของ repo เองยังไม่มีป้าย deprecated บอกด้วยซ้ำ (ซึ่งเป็นกับดัก — คนหลงเข้าไปเรื่อย ๆ) ใช้ **PSDK V3** แทนทุกกรณี

---

## 4. Cloud API / Edge SDK / FlightHub 2

### 4.1 Cloud API

**สถาปัตยกรรม (สำคัญที่สุด):** **โดรนต่อ third-party cloud โดยตรงไม่ได้** ต้องผ่าน **gateway device** ก่อน — คือ **DJI RC Plus** (ผ่าน DJI Pilot 2) หรือ **DJI Dock** แล้ว gateway จึงคุยกับ cloud

**Protocol:** MQTT + HTTPS + WebSocket (มาตรฐานทั่วไป ไม่ใช่ของ DJI เอง)

**ทำได้:**
- Wayline management: `flighttask_prepare` → `flighttask_execute` → cancel → รายงาน progress
- รองรับ mission type: waypoint, 2D/3D mapping, strip mapping, panorama (ใช้ **WPML** เหมือน MSDK)
- Dock 2 มี field **`wayline_precision_type`** เพิ่มมา
- Telemetry sync จาก dock + อากาศยานเข้า cloud ทันทีหลัง config
- Live stream, media upload, device management, firmware update, HMS (health management)

**ทำไม่ได้ / ข้อจำกัดจริง:**
- ไม่มี dock/RC Plus = ใช้ Cloud API ไม่ได้เลย (โดรนธรรมดาบินมือไม่เข้าข่าย)
- ก่อน takeoff ทุกครั้ง dock จะเช็คความสอดคล้องของ **"Offline Map"** และ **"Custom Flight Area"** ระหว่าง dock กับ cloud — ถ้า cloud ไม่ตอบ dock จะ **รอ timeout ประมาณ 40 วินาที** (ออกแบบ backend ต้องเผื่อ)

### 4.2 Edge SDK

Edge computing kit สำหรับ **DJI Dock** (รองรับทั้ง Dock และ Dock 2; มี Edge SDK V2 แล้ว) ทำได้:
- จัดการไฟล์ media ของอากาศยาน
- subscribe live stream ของอากาศยาน
- ช่องสื่อสาร local ที่ปลอดภัย
- SDK interconnection
- **รัน AI/video recognition บนเครื่อง local แบบ real-time** ← นี่คือจุดขายจริง: ประมวลผลภาพที่ dock ไม่ต้องส่งขึ้น cloud

**สำหรับงานคุณ:** ถ้าอนาคตทำเป็นระบบตรวจสะพานอัตโนมัติที่มี dock ประจำจุด Edge SDK คือที่ที่ deep learning model ของคุณจะรัน แต่**สำหรับ thesis ป.ตรี ที่บินมือ + ประมวลผลทีหลัง Edge SDK ไม่เกี่ยว**

### 4.3 FlightHub 2

- มี **On-Premises version** แล้ว (ติดตั้งในเซิร์ฟเวอร์ตัวเอง — สำคัญกับหน่วยงานราชการไทยที่ห้ามข้อมูลออกนอกประเทศ)
- **MQTT Bridge** — forward ข้อมูล MQTT ของ dock ไปยังระบบ third-party
- **RTSP output** — ดึงวิดีโอสดเข้าระบบ command center ของตัวเอง
- **OpenAPI** สำหรับ integrate โดยไม่ต้องสร้างเอง
- อัปเดตปี 2026: AI Copilot, Safesky airspace integration

---

## 5. UX SDK / Windows SDK

**Windows SDK: ตายแล้ว** — อยู่ในประกาศเดียวกัน 29 พ.ย. 2023 ที่หยุดอัปเดต iOS MSDK และ OSDK repo `dji-sdk/Windows-SDK` ยังอยู่บน GitHub แต่ไม่มีการพัฒนาต่อ **ห้ามเริ่มโปรเจกต์ใหม่ด้วยตัวนี้**

**UX SDK: ยังอยู่ แต่เปลี่ยนรูปแบบ**
- ใน MSDK V5 **UX SDK ไม่ใช่ SDK แยกอีกต่อไป** — มันมาเป็น **module `uxsdk` ในตัว sample repo** เลย เป็น pre-built UI widget (map, FPV view, camera setting, battery, RTK status, gimbal control ฯลฯ) ที่คุณ import แล้วใช้ได้ทันที หรือ fork ไปแก้ก็ได้เพราะโค้ดอยู่ในมือ
- repo เก่า `dji-sdk/Mobile-UXSDK-Android` (สาย V4, ค้างที่ beta) เป็น **legacy** ไม่ต้องใช้
- ฝั่ง **iOS UX SDK ตายตาม iOS MSDK**

**ผลกระทบกับคุณ:** ดีมาก — คุณไม่ต้องเขียน UI แผนที่/FPV/แบตเตอรี่เอง ดึง widget จาก `uxsdk` มาวางแล้วโฟกัสที่ logic การบิน + ประมวลผลภาพได้เลย ประหยัดเวลา thesis ไปเป็นเดือน

---

## 6. สรุปตรง ๆ ว่าอะไร "ทำไม่ได้"

| สิ่งที่ทำไม่ได้ | เหตุผล / หลักฐาน |
|---|---|
| **แก้/flash firmware เอง** | ไม่มี SDK ตัวไหนเปิดทาง firmware เป็น signed binary ปิดสนิท ผิด EULA ด้วย |
| **เข้าถึง flight controller ระดับต่ำ** | ไม่มี API สำหรับ motor PWM, attitude rate loop, หรือ control allocation สูงสุดที่ได้คือ **setpoint ระดับ velocity/attitude** ผ่าน Virtual Stick (MSDK) หรือ PSDK flight control (มี **Attitude Mode** สำหรับ M4E/4T ตั้งแต่ PSDK 3.16.0) |
| **เขียน custom EKF / state estimator ของตัวเอง** | ไม่ได้ — ไม่มีทางเสียบ estimator ตัวเองเข้า control loop และไม่มี raw IMU stream ความถี่สูงให้ ต่างจาก PX4/ArduPilot สิ้นเชิง **ถ้า thesis ต้องการเรื่องนี้ ต้องเปลี่ยนไปใช้ open-source flight stack** |
| **ปิด geofence / regulatory restricted zone** | Geofencing ฝังใน **firmware** ลบถาวรไม่ได้ Regulatory Restricted Zone (สนามบิน ฐานทัพ) **ล็อกระดับ firmware** ไม่ว่าจะทำอะไรก็บินไม่ได้ Enterprise ต้องขอ **Custom Unlock** ผ่าน FlySafe portal เท่านั้น (DJI เลิกบริการ self-unlock GEO แบบเดิมช่วงต้นปี 2026 และย้ายไป advisory model ตั้งแต่ พ.ย. 2025 ในหลายภูมิภาค — แต่ regulatory zone ยังล็อกเหมือนเดิม) |
| **ควบคุมโดรนใกล้ restricted zone ด้วยโค้ด** | เข้าใกล้ ~**30 m** → **RC ยึดคืน** virtual stick ตายทันที |
| **อ่าน raw stereo image pair จาก vision system** | ได้แค่ **ระยะที่ประมวลผลแล้ว** (`ObstacleData`, หน่วย mm, ช่องละ 1°) ไม่มีภาพดิบจากกล้อง fisheye ทั้ง 6 ตัว → ทำ visual SLAM ของตัวเองบนข้อมูลนี้ไม่ได้ |
| **อ่าน raw GNSS observables (pseudorange/carrier phase)** | MSDK เปิดเฉพาะ RTK **solution** + status ไม่ใช่ observables ดิบ → **confidence กลาง ยังไม่ยืนยัน 100%** ต้องตรวจใน `RTKCenterFragment.kt` ถ้าจะทำ post-processing PPK เอง |
| **พัฒนาบน iOS** | ตายตั้งแต่ 29 พ.ย. 2023 |
| **พัฒนาบน Windows** | ตายพร้อมกัน |
| **ใช้ Onboard SDK กับรุ่นใหม่** | ค้างที่ 4.1.0 (ก.พ. 2021) รองรับแค่ M300/M210 V2 |
| **register App Key แบบ offline** | MSDK ต้องต่อเน็ตไป verify กับ server DJI |
| **debug crash ระดับ native ใน SDK** | library เป็น `.so` ปิด — issue #794, #799 คือตัวอย่างที่ dev ทำได้แค่รอ DJI แก้ |
| **ใช้ consumer drone ส่วนใหญ่** | สาย consumer รองรับแค่ Mini 3 / Mini 3 Pro / Mini 4 Pro — และ Mini 3/3 Pro ยังไม่รองรับ obstacle avoidance แบบ BRAKE |

---

## 7. ตอบโจทย์เฉพาะหน้า: บินใกล้เสาตอม่อ + รู้ระยะห่าง + เก็บภาพไป stitch

### 7.1 "โดรนอยู่ห่างวัตถุเท่าไหร่" — มี 4 ทาง เรียงจากดีที่สุด

| วิธี | ความละเอียด/ช่วง | ข้อจำกัด |
|---|---|---|
| **1. LRF บน Zenmuse H30T/H20T** — `KeyLaserWorkMode`=`OPEN_ON_DEMAND` → `KeyLaserMeasureEnabled` → listen `KeyLaserMeasureInformation.targetDistance` | H30T: **3–3000 m**, ความแม่น **≤500 m: ±(0.2 m + ระยะ×0.15%)**, **>500 m: ±1.0 m** | **ระยะต่ำสุด 3 m** — ถ้าจะบินใกล้กว่านั้นตัวนี้ใช้ไม่ได้ วัดได้ทีละจุดตามที่ gimbal เล็ง ราคา payload สูง |
| **2. Perception ObstacleData** — `addObstacleDataListener`, `getHorizontalObstacleDistance()` | หน่วย **mm**, array **ช่องละ 1°** รอบตัว (0°=หัวเครื่อง), ค่า **60000 = ไม่พบ** | เป็นค่าจากระบบหลบสิ่งกีดขวาง ไม่ได้ออกแบบมาให้แม่นระดับ metrology; ช่วงใช้งานตามรุ่น |
| **3. Vision system spec ของ M4E/M4T** | Forward/Backward binocular **0.4–22.5 m** (รวม **0.4–200 m**), Lateral **0.5–32 m**, Downward **0.3–18.8 m** | บอกได้ว่าใกล้เกิน 0.4 m ระบบมองไม่เห็น = อันตราย |
| **4. LiDAR ของ Matrice 400** (rotating LiDAR) | **0.5–100 m** @ 100,000 lux, reflectivity 10%; **520,000 จุด/วินาที**; 905 nm; **Class 1** eye-safe; mmWave radar FOV **±45°** | เครื่องแพงมาก แต่นี่คือทางเดียวที่ได้ point cloud ระยะใกล้จริง ๆ จาก DJI |

**คำแนะนำสำหรับ thesis:** ใช้ **วิธี 2 (ObstacleData)** เป็น safety envelope real-time + **วิธี 1 (LRF)** ถ้ามี H30T สำหรับวัดระยะจุดที่สนใจ แล้วบันทึกทั้งคู่ลง log พร้อม timestamp ของภาพ → คุณจะมี ground-truth ระยะสำหรับคำนวณ GSD ของทุกภาพ ซึ่งเป็นสิ่งที่งานวิจัย crack detection ต้องการมากที่สุด (ความกว้างรอยแตกเป็น mm แปลงจาก pixel ได้ต่อเมื่อรู้ระยะ)

### 7.2 "บินใกล้ขึ้น" — ทำได้แค่ไหน

1. **ลด braking distance** ผ่าน `setObstacleAvoidanceBrakingDistance()` — M30 ตั้งได้ต่ำสุด **1.0 m** แนวราบ (`[1.0, 10.0]`) และ warning ต่ำสุด **1.1 m** (`[1.1, 33.0]`) นี่คือวิธีที่ปลอดภัยที่สุดในการบินใกล้ขึ้น
2. **`setObstacleAvoidanceType(CLOSE)`** — ปิดหลบสิ่งกีดขวางทั้งหมด บินได้ใกล้เท่าที่นักบินกล้า **แต่นี่คือการปิดตาข่ายนิรภัยตัวสุดท้าย** ถ้าจะทำต้องมี visual observer และซ้อมบนที่โล่งก่อน
3. **Virtual Stick advanced mode** ส่ง velocity setpoint 5–25 Hz พร้อม wind compensation — แต่ **obstacle avoidance จะทำงานเฉพาะเมื่อ vertical=velocity, yaw=angular velocity, roll/pitch=velocity** เท่านั้น ถ้าคุณใช้ position mode จะไม่มีตัวช่วยเลย
4. **ห้ามลืม:** Mini 3/3 Pro **ปรับพวกนี้ไม่ได้** ต้องใช้ Enterprise (M30/M3E/M350/M4E) เท่านั้น

### 7.3 กับดักใหญ่ที่สุดของงานตรวจสะพาน: **ใต้สะพาน GPS หาย**

นี่คือสิ่งที่ต้องรู้ก่อนออกแบบระบบทั้งหมด — งานวิจัยที่ผ่าน peer review ระบุตรง ๆ:

- **Waypoint mission ใช้ไม่ได้ใต้ deck สะพาน** เพราะ WPML mission อาศัยพิกัด GNSS
- **Alaska DOT** พบว่า DJI Phantom **เสียตำแหน่งเมื่อบินเข้าใกล้ผิวที่ตรวจ** สันนิษฐานว่า **เหล็กเสริมในพื้นคอนกรีตรบกวน magnetometer และ IMU**
- **Idaho DOT** บิน DJI Mavic ใต้สะพานข้ามแม่น้ำแล้ว **เครื่องไม่นิ่ง เพราะ downward vision/sonar สับสนกับน้ำที่ไหล**
- Vision positioning ทำงานได้ถ้าพื้นผิวมี feature ชัดและแสงพอ แต่ **drift ระดับ ~5 cm ถือว่าปกติ** — สำหรับ structural monitoring ที่ต้องเทียบภาพข้ามรอบเวลา นี่อาจยอมรับไม่ได้

**ทางออกที่เป็นจริง 3 ทาง:**

- **(ก) จำกัด scope ที่ "เสาตอม่อและด้านข้าง"** ซึ่งยังเห็นฟ้า → RTK ทำงานได้ → waypoint mission ทำงานได้ → นี่คือ scope ที่ทำสำเร็จได้จริงในเวลาของ thesis **แนะนำทางนี้**
- **(ข) ใต้ deck ใช้บินมือ + บันทึกภาพ** แล้วพึ่ง **SfM/photogrammetry** สร้างตำแหน่งกล้องย้อนหลัง (ไม่ต้องพึ่ง GPS ตอนบิน) — ให้ผลดีถ้ามี overlap พอ แต่ควบคุมความสม่ำเสมอยาก
- **(ค) ถ้าจำเป็นต้อง GPS-denied จริงจัง** โดรนที่ออกแบบมาเพื่อการนี้คือ **Flyability Elios 3** (LiDAR SLAM, มีกรง) หรือ **Voliro T** — **ไม่ใช่ DJI** ถ้า thesis ต้องการเข้าไปใต้ deck จริง ๆ ควรระบุข้อจำกัดนี้ในบทที่ 3 แทนที่จะพยายามบังคับ DJI ให้ทำสิ่งที่มันทำไม่ได้

### 7.4 การเก็บภาพเพื่อ stitching/photogrammetry

- **ใช้ WPML action ในไฟล์ KMZ** ตั้ง gimbal pitch (เงยขึ้นถ่ายใต้คาน), hover, ถ่ายภาพ ที่ทุก waypoint — สร้างด้วย `IWPMZManager.generateKMZFile()` แล้ว `pushKMZFileToAircraft()`
- **อย่าลืม `waylines.wpml`** — firmware execute ไฟล์นี้ ไม่ใช่ `template.kml`
- **M300/M350 RTK ใช้ได้แค่ 1 wayline ID ต่อ mission** — ถ้าจะบินหลายชั้นความสูงต้องแยกเป็นหลาย mission
- **RTK เปิดไว้เสมอ** เพื่อให้ geotag แม่นระดับ cm → point cloud มี scale จริง ไม่ต้องพึ่ง GCP มาก
- **GSD ต้องคำนวณย้อนกลับจากความกว้างรอยแตกที่ต้องตรวจ:**

  ```
  GSD (mm/px) = (ระยะห่าง × sensor pixel pitch) / focal length
  ```

  แล้วเลือกระยะบินจาก GSD ที่ต้องการ **ตัวเลข sensor pixel pitch/focal length ของ M4E/M3E ต้องดึงจาก spec sheet ทางการเอง — ผมไม่ยืนยันตัวเลขให้** และหลักการ "ต้องมีกี่ pixel ต่อความกว้างรอยแตกจึงจะตรวจได้" เป็น engineering heuristic ที่**คุณต้อง validate ด้วย dataset ของตัวเอง** ไม่ใช่ค่าคงที่ที่อ้างอิงมาตรฐานได้ — เรื่องนี้เองน่าจะเป็น contribution หนึ่งของ thesis คุณ (ผูกกับเกณฑ์ความกว้างรอยแตกใน BMMS/T-BHI ได้ตรง ๆ)

### 7.5 สถาปัตยกรรมที่แนะนำสำหรับ ku_project_jop

```
Android app (MSDK V5.18.0, Kotlin)
├── IWPMZManager        → สร้าง KMZ จาก scan pattern ที่คำนวณจาก GSD เป้าหมาย
├── IWaypointMissionManager → push + start + ติดตาม WaylineExecutingInfoListener
├── IPerceptionManager  → log ObstacleData (mm, ต่อ 1°) ทุก frame = ระยะจริงถึงผิวเสา
├── KeyLaserMeasureInformation (ถ้ามี H30T) → ระยะจุดที่ gimbal เล็ง
├── KeyManager (CameraKey) → สั่งถ่าย + อ่าน metadata
├── MediaManager        → ดึงภาพลง tablet หลังบินเสร็จ
├── ISimulatorManager   → ทดสอบ mission logic โดยไม่ต้องบินจริง (ทำก่อนทุกครั้ง!)
└── uxsdk widgets       → UI ไม่ต้องเขียนเอง

Offline (PC)
├── SfM/photogrammetry (DJI Terra หรือ open-source: COLMAP/OpenDroneMap)
├── Crack detection model (ของคุณ)
└── mapping ผล → condition rating ตาม T-BHI / BMMS
```

**ทำ Simulator ให้ผ่านก่อนบินจริงทุกครั้ง** — `ISimulatorManager.enableSimulator()` มีให้ใช้ฟรี และ mission ที่พังบน simulator จะพังบนของจริงเหมือนกัน แต่ราคาต่างกันหลายแสน

---

## สรุปคำตอบใน 5 บรรทัด

1. **ลง software ลงตัวโดรนตรง ๆ ไม่ได้** — เขียนได้แค่ Android app (MSDK V5.18.0) กับ payload computer (PSDK V3.16.0)
2. **iOS / Windows SDK / Onboard SDK ตายหมดตั้งแต่ 29 พ.ย. 2023** — Android เท่านั้น
3. **สำหรับ thesis คุณ MSDK V5 พอแล้ว** ไม่ต้องแตะ PSDK เว้นแต่จะแขวนเซนเซอร์ตัวเองขึ้นไป
4. **วัดระยะ:** ObstacleData (mm, ทุก 1°) + LRF (3–3000 m, ±0.2 m+0.15%) — พอสำหรับ GSD-aware flight
5. **ใต้ deck สะพาน DJI ไปไม่ถึง** — จำกัด scope ที่เสาตอม่อ/ด้านข้างที่ยังเห็นฟ้า แล้วระบุข้อจำกัดนี้ใน methodology ตรง ๆ จะได้ thesis ที่แข็งกว่าการฝืน


## KEY NUMBERS
- MSDK V5 เวอร์ชันล่าสุด: 5.18.0  [high] https://github.com/dji-sdk/Mobile-SDK-Android-V5/blob/dev-sdk-main/README.md
- MSDK V5 artifact บน Maven Central: com.dji:dji-sdk-v5-aircraft 5.18.0  [high] https://central.sonatype.com/artifact/com.dji/dji-sdk-v5-aircraft
- วันที่เผยแพร่เอกสาร Android MSDK 5.18.0 Release Notes: 22 พ.ค. 2026  [medium] https://developer.dji.com/doc/mobile-sdk-tutorial/en/
- DJI หยุดอัปเดต iOS Mobile SDK / Windows SDK / Onboard SDK: มีผล 29 พ.ย. 2023  [high] https://sdk-forum.dji.net/hc/en-us/articles/25786229596057-Part-of-DJI-SDK-stops-updating-announcement
- Onboard SDK เวอร์ชันสุดท้าย: OSDK 4.1.0 ปล่อย 2 ก.พ. 2021  [high] https://github.com/dji-sdk/Onboard-SDK
- Onboard SDK รุ่นที่รองรับ: M300 RTK, M210 RTK V2, M210 V2  [high] https://github.com/dji-sdk/Onboard-SDK
- PSDK เวอร์ชันล่าสุดและวันที่: 3.16.0, 1 เม.ย. 2026  [high] https://github.com/dji-sdk/Payload-SDK/releases
- PSDK 3.12.0 เพิ่ม E-PORT V2 พร้อมตัวเลือกไฟ: 13.6 V / 17 V / 24 V (ปล่อย 27 มิ.ย. 2025)  [high] https://github.com/dji-sdk/Payload-SDK/releases
- E-Port V2 Development Board ขนาด: 89 × 60 × 13.4 mm  [high] https://dl.djicdn.com/downloads/Matrice_400/DJI_E_Port_V2_Development_Kit_Product_Information.pdf
- E-Port V2 Dev Kit — XT30 VCC output: 13.8 V / 17.02 V / 24 V, 5 A  [high] https://dl.djicdn.com/downloads/Matrice_400/DJI_E_Port_V2_Development_Kit_Product_Information.pdf
- E-Port V2 Dev Kit — XT30 12 V output: 12 V / 4 A  [high] https://dl.djicdn.com/downloads/Matrice_400/DJI_E_Port_V2_Development_Kit_Product_Information.pdf
- E-Port V2 Dev Kit — XT30 5 V output: 5 V / 4 A  [high] https://dl.djicdn.com/downloads/Matrice_400/DJI_E_Port_V2_Development_Kit_Product_Information.pdf
- E-Port (V1) Adapter Board ขนาด: 55 × 40 × 9 mm  [medium] https://store.hp-drones.com/en/dji-matrice-300-rtk/1900-D961945-6941565961945.html
- E-Port XT30 VCC output — Mavic 3E/3T: 12–17.6 V / 4 A  [medium] https://store.hp-drones.com/en/dji-matrice-300-rtk/1900-D961945-6941565961945.html
- E-Port XT30 VCC output — Matrice 30 Series: 19.2–26.1 V / 4 A  [medium] https://store.hp-drones.com/en/dji-matrice-300-rtk/1900-D961945-6941565961945.html
- E-Port XT30 VCC output — M300 RTK / M350 RTK: 24 V / 4 A  [medium] https://store.hp-drones.com/en/dji-matrice-300-rtk/1900-D961945-6941565961945.html
- E-Port XT30 12 V / 5 V output: 12 V / 2 A และ 5 V / 2 A  [medium] https://store.hp-drones.com/en/dji-matrice-300-rtk/1900-D961945-6941565961945.html
- SkyPort V3 แรงดันที่ request ได้: 13.6 V, 17 V, 24 V  [medium] https://developer.dji.com/doc/payload-sdk-tutorial/en/quick-start/quick-guide/E-Port%20V2.html
- SkyPort V3 รองรับเฉพาะอากาศยาน: Matrice 400 เท่านั้น (ไม่รองรับ M300/M350)  [medium] https://developer.dji.com/doc/payload-sdk-tutorial/en/quick-start/quick-guide/E-Port%20V2.html
- SkyPort V3 link mode ที่รองรับ: ONLY_USB_BULK และ ONLY_NETWORK (ไม่รองรับ UART_AND_NETWORK / UART_AND_USB_BULK)  [medium] https://developer.dji.com/doc/payload-sdk-tutorial/en/quick-start/quick-guide/E-Port%20V2.html
- ราคา DJI E-Port Development Kit: 133 USD  [medium] https://globaldronehq.com/products/dji-e-port-development-kit
- IPerceptionManager — M30 horizontal warning distance range: [1.1, 33.0] m  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager.html
- IPerceptionManager — M30 downward warning distance range: [0.6, 33.0] m  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager.html
- IPerceptionManager — M30 horizontal braking distance range: [1.0, 10.0] m  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager.html
- IPerceptionManager — M30 downward braking distance range: [0.5, 3.0] m  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager.html
- setPrecisionLandingEnabled ต้อง takeoff สูงอย่างน้อย: 7 m  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager.html
- setOverallObstacleAvoidanceEnabled ถูก deprecate ตั้งแต่: MSDK 5.1.0  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager.html
- ObstacleData หน่วยของระยะสิ่งกีดขวาง: millimeter (mm)  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager_ObstacleData.html
- ObstacleData ค่าที่แปลว่าไม่พบสิ่งกีดขวาง และช่วงเชิงมุมต่อ index: 60000 = ไม่พบ; array ช่องละ 1 องศา (0° = หัวเครื่อง, 90° = ขวา, 180° = ท้าย)  [medium] https://sdk-forum.dji.net/hc/en-us/articles/4418315942169-How-to-get-the-visual-obstacle-avoidance-data
- Virtual Stick advanced mode ความถี่ส่งที่แนะนำ: 5–25 Hz  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IVirtualStickManager/IVirtualStickManager.html
- Virtual Stick — ระยะที่ RC ยึดการควบคุมคืนใกล้ restricted zone: ประมาณ 30 m  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IVirtualStickManager/IVirtualStickManager.html
- Virtual Stick — รุ่นที่รองรับ obstacle avoidance ระหว่างใช้ virtual stick: M300 RTK, M350 RTK, M30 series, Mavic 3E series, Mavic 3M  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IVirtualStickManager/IVirtualStickManager.html
- Virtual Stick — firmware ต่ำกว่าค่านี้ obstacle sensing ถูกปิด: V7.01.10.03  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IVirtualStickManager/IVirtualStickManager.html
- IWaypointMissionManager — จำนวน wayline ID ที่ M300/M350 RTK รองรับ: 1 wayline ID เท่านั้น  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IWaypointMissionManager/IWaypointMissionManager.html
- KMZ ที่ MSDK V5 ใช้ ต้องมีไฟล์: waylines.wpml (firmware execute ไฟล์นี้)  [high] https://developer.dji.com/doc/mobile-sdk-tutorial/en/tutorials/waypoint.html
- Zenmuse H30T laser rangefinder ช่วงวัด: 3–3000 m  [medium] https://enterprise.dji.com/zenmuse-h30-series
- Zenmuse H30T LRF ความแม่นยำ: ≤500 m: ±(0.2 m + ระยะ × 0.15%); >500 m: ±1.0 m  [medium] https://advexure.com/blogs/news/dji-zenmuse-h30t-everything-you-need-to-know
- Matrice 4E/4T forward/backward binocular measurement range: 0.4–22.5 m (overall 0.4–200 m), FOV 90° H × 135° V  [medium] https://enterprise.dji.com/matrice-4-series/specs
- Matrice 4E/4T lateral measurement range: 0.5–32 m (overall 0.5–200 m), FOV 90° H × 90° V  [medium] https://enterprise.dji.com/matrice-4-series/specs
- Matrice 4E/4T downward measurement range: 0.3–18.8 m  [medium] https://enterprise.dji.com/matrice-4-series/specs
- Matrice 400 rotating LiDAR ช่วงวัดมาตรฐาน: 0.5–100 m @ 100,000 lux, reflectivity 10%  [medium] https://enterprise.dji.com/matrice-400/specs
- Matrice 400 LiDAR point rate / wavelength / eye safety: 520,000 จุด/วินาที, 905 nm, Class 1 (IEC60825-1:2014)  [medium] https://enterprise.dji.com/matrice-400/specs
- Matrice 400 mmWave radar FOV: ±45° ทั้งแนวราบและแนวดิ่ง  [medium] https://enterprise.dji.com/matrice-400/specs
- Cloud API — เวลา timeout ที่ dock รอ cloud ตอบเรื่อง Offline Map / Custom Flight Area ก่อน takeoff: ประมาณ 40 วินาที  [medium] https://github.com/dji-sdk/Cloud-API-Doc/blob/master/docs/en/80.faq.md
- Cloud API — โดรนต่อ third-party cloud ตรงไม่ได้: ต้องผ่าน gateway (DJI RC Plus ผ่าน Pilot 2 หรือ DJI Dock)  [high] https://github.com/dji-sdk/Cloud-API-Doc/blob/master/docs/en/10.overview/20.product-architecture.md
- MSDK V5 รุ่นอากาศยานที่รองรับ (README 5.18.0): Mavic 3TA, Matrice 400, Matrice 4D Enterprise Series, Matrice 4 Enterprise Series, Mini 4 Pro, Mini 3 Pro, Mini 3, Mavic 3 Enterprise Series, M30 Series, M300 RTK, Matrice 350 RTK, H30 Series  [high] https://github.com/dji-sdk/Mobile-SDK-Android-V5/blob/dev-sdk-main/README.md
- Mini 3 / Mini 3 Pro ไม่รองรับ obstacle avoidance แบบ BRAKE: เปิด/ปิด sub-switch ไม่ได้  [high] https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager.html
- PSDK รองรับ platform พัฒนา: Linux (ARM64 / ARM32 / x86_64) และ RTOS (ARM Cortex-M4 + FreeRTOS, ตัวอย่าง STM32F4 Discovery)  [medium] https://deepwiki.com/dji-sdk/Payload-SDK
- Regulatory Restricted Zone ของ DJI ล็อกที่ระดับ firmware: บินไม่ได้ไม่ว่าจะ unlock อย่างไร; DJI เลิกบริการ self-unlock GEO เดิมช่วงต้นปี 2026  [medium] https://dronesgator.com/how-to-unlock-dji-geofencing
- งานวิจัยยืนยันปัญหาบินใต้ deck สะพาน: Alaska DOT: DJI Phantom เสียตำแหน่งเมื่อเข้าใกล้ผิวตรวจ (เหล็กเสริมรบกวน magnetometer/IMU); Idaho DOT: DJI Mavic ไม่นิ่งเพราะ downward vision/sonar สับสนกับน้ำไหล  [high] https://doi.org/10.3390/drones6030064

## SOURCES
- https://github.com/dji-sdk/Mobile-SDK-Android-V5
- https://github.com/dji-sdk/Mobile-SDK-Android-V5/blob/dev-sdk-main/README.md
- https://github.com/dji-sdk/Mobile-SDK-Android-V5/issues
- https://github.com/dji-sdk/Mobile-SDK-Android-V5/tree/dev-sdk-main/SampleCode-V5/android-sdk-v5-sample/src/main/java/dji/sampleV5/aircraft/pages
- https://central.sonatype.com/artifact/com.dji/dji-sdk-v5-aircraft
- https://developer.dji.com/doc/mobile-sdk-tutorial/en/
- https://developer.dji.com/doc/mobile-sdk-tutorial/en/tutorials/waypoint.html
- https://developer.dji.com/doc/mobile-sdk-tutorial/en/tutorials/perception.html
- https://developer.dji.com/doc/mobile-sdk-tutorial/en/tutorials/virtual-stick.html
- https://developer.dji.com/api-reference-v5/android-api/Components/IWaypointMissionManager/IWaypointMissionManager.html
- https://developer.dji.com/api-reference-v5/android-api/Components/IVirtualStickManager/IVirtualStickManager.html
- https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager.html
- https://developer.dji.com/api-reference-v5/android-api/Components/IPerceptionManager/IPerceptionManager_ObstacleData.html
- https://developer.dji.com/api-reference-v5/android-api/Components/ISimulatorManager/ISimulatorManager.html
- https://developer.dji.com/api-reference/android-api/Components/Camera/DJICamera_DJICameraLaserMeasureInformation.html
- https://developer.dji.com/mobile-sdk/documentation/quick-start/index.html
- https://developer.dji.com/mobile-sdk/documentation/application-development-workflow/workflow-register.html
- https://developer.dji.com/policies/eula/
- https://sdk-forum.dji.net/hc/en-us/articles/25786229596057-Part-of-DJI-SDK-stops-updating-announcement
- https://sdk-forum.dji.net/hc/en-us/articles/4418315942169-How-to-get-the-visual-obstacle-avoidance-data
- https://sdk-forum.dji.net/hc/en-us/articles/9882785690009-Chapter-16-Visual-obstacle-avoidance-system
- https://dronedj.com/2023/11/30/dji-ios-sdk-android-app/
- https://coptrz.com/blog/from-ios-to-android-why-dji-dropped-ios-support-for-developers/
- https://github.com/dji-sdk/Payload-SDK
- https://github.com/dji-sdk/Payload-SDK/releases
- https://deepwiki.com/dji-sdk/Payload-SDK
- https://developer.dji.com/payload-sdk/
- https://developer.dji.com/doc/payload-sdk-tutorial/en/quick-start/quick-guide/E-Port%20V2.html
- https://developer.dji.com/doc/payload-sdk-tutorial/en/model-instruction/choose-hardware-platform.html
- https://developer.dji.com/doc/payload-sdk-tutorial/en/development-preparation/development-platform-overview/development-kit-overview.html
- https://dl.djicdn.com/downloads/Matrice_400/DJI_E_Port_V2_Development_Kit_Product_Information.pdf
- https://store.hp-drones.com/en/dji-matrice-300-rtk/1900-D961945-6941565961945.html
- https://globaldronehq.com/products/dji-e-port-development-kit
- https://store.dji.com/product/dji-skyport-adapter-set-v2
- https://github.com/dji-sdk/Onboard-SDK
- https://developer.dji.com/onboard-sdk/documentation/appendix/releaseNotes.html
- https://github.com/dji-sdk/Edge-SDK
- https://developer.dji.com/doc/edge-sdk-tutorial/en/basic-intro/whats-esdk.html
- https://github.com/dji-sdk/Edge-SDK-V2-Tutorial
- https://github.com/dji-sdk/Cloud-API-Doc/blob/master/docs/en/10.overview/20.product-architecture.md
- https://github.com/dji-sdk/Cloud-API-Doc/blob/master/docs/en/80.faq.md
- https://developer.dji.com/doc/cloud-api-tutorial/en/api-reference/dock-to-cloud/mqtt/dock/dock2/wayline.html
- https://fh.dji.com/user-manual/en/release-notes/release-notes-private.html
- https://enterprise-insights.dji.com/blog/dji-flighthub-2-on-premises-officially-released
- https://enterprise-insights.dji.com/blog/dji-flighthub-2-latest-update-ai-copilot-2026
- https://github.com/dji-sdk/Windows-SDK
- https://github.com/dji-sdk/Mobile-UXSDK-Android
- https://enterprise.dji.com/matrice-4-series/specs
- https://enterprise.dji.com/matrice-400/specs
- https://enterprise.dji.com/zenmuse-h30-series
- https://advexure.com/blogs/news/dji-zenmuse-h30t-everything-you-need-to-know
- https://doi.org/10.3390/drones6030064
- https://enterprise-insights.dji.com/blog/dji-drone-self-unlock-nfz-geo-zone
- https://dronesgator.com/how-to-unlock-dji-geofencing
- https://www.dronepilotgroundschool.com/dji-unlocking-geofence/
- https://enterprise-insights.dji.com/blog/dji-sdk-guide
- https://support.dji.com/help/content?customId=01700000763&documentType=&lang=en&paperDocType=ARTICLE&re=US&spaceId=17
- https://uavcoach.com/bridge-drone/

## OPEN QUESTIONS
- Bandwidth จริงของ E-Port / E-Port V2 / SkyPort V3 (Mbps) — ไม่พบตัวเลขทางการ ต้องเปิด https://developer.dji.com/doc/payload-sdk-tutorial/en/model-instruction/choose-hardware-platform.html ในเบราว์เซอร์จริง (หน้า render ด้วย JS ดึงผ่าน HTTP ธรรมดาไม่ได้) หรือถาม DJI SDK support โดยตรง
- ราคา E-Port V2 Development Kit / SkyPort V2 Adapter Set / X-Port — ผู้ขายส่วนใหญ่ไม่ประกาศราคาสาธารณะ (บางรายระบุว่า DJI ห้ามโฆษณาราคา) ต้องติดต่อ dealer ที่ได้รับอนุญาตในไทย
- minSdkVersion / JDK / Gradle version ที่ MSDK 5.18.0 ต้องใช้ — README ไม่ระบุ ต้องดู build.gradle ใน SampleCode-V5/android-sdk-v5-sample/
- ชื่อคลาสจริงของ RTK manager, LiveStream manager, Media manager ใน MSDK V5 — URL API reference ที่เดาไว้ตอบ 404 ต้องเปิดจากซอร์ส RTKCenterFragment.kt / LiveFragment.kt / MediaFragment.kt ใน repo
- LiveStream protocol ที่ MSDK V5 รองรับจริง (RTMP / RTSP / GB28181 / Agora) — ยังไม่ได้ยืนยันจากเอกสารทางการในรอบนี้
- MSDK V5 เปิด raw GNSS observables (pseudorange / carrier phase) สำหรับทำ PPK เองหรือไม่ — เชื่อว่าไม่ แต่ยังไม่ยืนยัน ต้องตรวจใน RTKCenterFragment.kt
- มาตรฐาน C ที่ PSDK V3 ต้องการ (C99 / C11) — ต้องดู CMakeLists.txt ใน repo dji-sdk/Payload-SDK
- กระบวนการ certification / partner agreement สำหรับผลิต PSDK payload เชิงพาณิชย์ — ไม่พบเอกสารสาธารณะ ต้องติดต่อ DJI SDK support
- sensor pixel pitch และ focal length ของกล้อง M4E/M3E เพื่อคำนวณ GSD — ต้องดึงจาก spec sheet ทางการของแต่ละรุ่นโดยตรง อย่าใช้ตัวเลขประมาณ
- ระยะบินขั้นต่ำที่ปลอดภัยจริงสำหรับตรวจรอยแตกเสาตอม่อ และ GSD ที่ต้องการต่อความกว้างรอยแตกตามเกณฑ์ BMMS/T-BHI — ไม่มีค่ามาตรฐานอ้างอิงได้ ต้อง validate ด้วย dataset ของโครงการเอง (น่าจะเป็น contribution หนึ่งของ thesis)
- กฎหมายไทย: การบินใกล้โครงสร้างสาธารณะ/สะพาน ต้องขออนุญาต กสทช. + CAAT อย่างไร และมี restricted zone ทับซ้อนหรือไม่ — อยู่นอกขอบเขตการค้นรอบนี้ ต้องตรวจกับ CAAT ก่อนบินจริง
