import json, math, collections
rows = json.load(open('meta_raw.json', encoding='utf-8'))
lat0 = float(rows[0]['xmp']['drone-dji:GpsLatitude']); lon0 = float(rows[0]['xmp']['drone-dji:GpsLongitude'])
print('models', collections.Counter(r['xmp'].get('drone-dji:DroneModel') for r in rows), 'GpsStatus', collections.Counter(r['xmp'].get('drone-dji:GpsStatus') for r in rows),
      'EXIF GPSStatus', collections.Counter(r['gps'].get('GPSStatus') for r in rows), 'AltType', collections.Counter(r['xmp'].get('drone-dji:AltitudeType') for r in rows))
print('lat0 lon0', lat0, lon0)
print(f"{'name':22s} {'time':19s} {'sub':>4s} {'E(m)':>8s} {'N(m)':>8s} {'relAlt':>6s} {'absAlt':>7s} {'gYaw':>7s} {'gPit':>6s} {'gRol':>5s} {'fYaw':>7s} {'vx':>5s} {'vy':>5s} {'vz':>5s} fl dz")
for r in rows:
    x = r['xmp']; lat = float(x['drone-dji:GpsLatitude']); lon = float(x['drone-dji:GpsLongitude'])
    N = (lat - lat0) * 111320.0; E = (lon - lon0) * 111320.0 * math.cos(math.radians(lat0))
    r['E'] = E; r['N'] = N
    print(f"{r['name']:22s} {r['dto']:19s} {str(r['subsec']):>4s} {E:8.2f} {N:8.2f} {x['drone-dji:RelativeAltitude']:>6s} {x['drone-dji:AbsoluteAltitude']:>7s} {x['drone-dji:GimbalYawDegree']:>7s} {x['drone-dji:GimbalPitchDegree']:>6s} {x['drone-dji:GimbalRollDegree']:>5s} {x['drone-dji:FlightYawDegree']:>7s} {x['drone-dji:FlightXSpeed']:>5s} {x['drone-dji:FlightYSpeed']:>5s} {x['drone-dji:FlightZSpeed']:>5s} {r['fl']} {r['dz']}")
json.dump(rows, open('meta.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
