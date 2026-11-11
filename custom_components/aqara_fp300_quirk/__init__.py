"""Aqara FP300 (lumi.sensor_occupy.agl8) ZHA quirk loader.

Stock ZHA in HA <= 2026.8 has no handler for the Aqara FP300, so it exposes only
temperature/humidity/illuminance and misses the mmWave presence + PIR motion,
which the device reports on its private 0xFCC0 cluster.

This integration vendors the v2 zigpy quirk from zha-device-handlers PR #4504
(cemizm) and registers it at import time, so ZHA gains:
  * binary_sensor  <name>_occupancy   (mmWave presence, device_class OCCUPANCY)
  * binary_sensor  <name>_motion      (PIR, device_class MOTION)
  * corrected battery %, plus sensitivity / detection-range / LED config entities.

HA 2026.11 (zha 2.4.x, zha-quirks 2.4.x) ships its own *basic* FP300 quirk
(zha-device-handlers PR #5530, module ``zhaquirks.xiaomi.aqara.motion_agl8``)
with only occupancy + motion. ZHA's registry lets the most recently registered
quirk win, and HA imports this package before ZHA walks the built-in quirks, so
the basic quirk won and every config entity of ours went "unavailable".
Fix: import the built-in module ourselves first (Python caches it, so ZHA's
later walk does not register it again), drop its registry entry, then register
ours. On older ZHA without the built-in module this is a no-op.

The quirk registers as soon as this package is imported (HA imports it during
setup). After install + HA restart, re-interview the FP300 once if ZHA does not
rebuild it against the now-registered quirk.
"""

import importlib
import logging

_LOGGER = logging.getLogger(__name__)

MANUFACTURER = "Aqara"
MODEL = "lumi.sensor_occupy.agl8"
UPSTREAM_MODULE = "zhaquirks.xiaomi.aqara.motion_agl8"


def evict_upstream_quirk() -> int:
    """Pre-import the built-in basic FP300 quirk and remove it from ZHA's registry.

    Returns the number of registry entries removed (0 when ZHA has no built-in
    FP300 quirk or no new-style registry).
    """
    try:
        importlib.import_module(UPSTREAM_MODULE)
    except ImportError:
        return 0
    try:
        from zha.quirks import DEVICE_REGISTRY, ModelInfo
    except ImportError:
        return 0
    entries = DEVICE_REGISTRY._registry.get(ModelInfo(MANUFACTURER, MODEL), [])
    removed = 0
    for entry in list(entries):
        if getattr(entry.source, "module", None) == UPSTREAM_MODULE:
            DEVICE_REGISTRY.remove(entry)
            removed += 1
    return removed


try:
    _removed = evict_upstream_quirk()
    if _removed:
        _LOGGER.info("Removed %d built-in basic FP300 quirk entr(y/ies) in favour of the full quirk", _removed)
except Exception:  # pragma: no cover - never block our own registration
    _LOGGER.exception("Could not remove the built-in FP300 quirk; ours may be shadowed")

# Importing the module executes its module-level QuirkBuilder(...).add_to_registry(),
# which inserts the FP300 quirk into ZHA's quirk registry.
try:
    from . import motion_agl8  # noqa: F401

    _LOGGER.info("Aqara FP300 ZHA quirk registered (Aqara / lumi.sensor_occupy.agl8)")
except Exception:  # pragma: no cover - defensive; surfaced in the HA log
    _LOGGER.exception("Failed to register the Aqara FP300 ZHA quirk")


async def async_setup_entry(hass, entry) -> bool:
    """No runtime work: the quirk is registered at import (above)."""
    return True


async def async_unload_entry(hass, entry) -> bool:
    """Nothing to tear down. The quirk stays registered for the process lifetime."""
    return True