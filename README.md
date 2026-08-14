# Aqara FP300 ZHA Quirk (`lumi.sensor_occupy.agl8`)

A tiny Home Assistant custom integration that registers a **ZHA quirk** for the
**Aqara FP300** presence sensor.

## Why

Stock ZHA (through HA 2026.8) has no handler for the FP300. On join it exposes
only temperature, humidity and illuminance — the **mmWave presence** and **PIR
motion** live on Aqara's private `0xFCC0` cluster and are silently ignored, and
battery reports 0 %.

## What it adds

Once loaded, ZHA re-interviews the device against the quirk and creates:

- `binary_sensor.<name>_occupancy` — mmWave presence (`device_class: occupancy`)
- `binary_sensor.<name>_motion` — PIR (`device_class: motion`)
- corrected **battery %** (derived from voltage)
- config entities: motion sensitivity, presence detection mode, absence delay,
  per-metre detection-range switches, AI adaptive sensitivity, LED schedule, and
  maintenance buttons (spatial learning / restart).

## Credit

The quirk itself is vendored verbatim from
[zha-device-handlers PR #4504](https://github.com/zigpy/zha-device-handlers/pull/4504)
by **@cemizm**. This repo only wraps it so it can be installed via HACS and kept
registered without editing `configuration.yaml`. When that PR is merged into a
released ZHA, remove this integration and use stock support.

## Install

1. HACS → custom repository → this repo (category: *Integration*) → Download.
2. Restart Home Assistant.
3. Settings → Devices & Services → **Add Integration** → "Aqara FP300 ZHA Quirk".
4. ZHA → the FP300 device → **Reconfigure / re-interview** once so the new
   entities appear. (Wake the sensor if it's asleep.)

## Note on restarts

The quirk registers when the integration loads. Because a networked ZHA
coordinator initialises slowly, registration normally wins the race and the
entities survive restarts. If presence ever reads *unavailable* after an HA
restart, reload the **ZHA** integration once (rebuilds devices from cache — no
device interaction needed).
