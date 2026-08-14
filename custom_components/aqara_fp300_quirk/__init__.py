"""Aqara FP300 (lumi.sensor_occupy.agl8) ZHA quirk loader.

Stock ZHA in HA <= 2026.8 has no handler for the Aqara FP300, so it exposes only
temperature/humidity/illuminance and misses the mmWave presence + PIR motion,
which the device reports on its private 0xFCC0 cluster.

This integration vendors the v2 zigpy quirk from zha-device-handlers PR #4504
(cemizm) and registers it at import time, so ZHA gains:
  * binary_sensor  <name>_occupancy   (mmWave presence, device_class OCCUPANCY)
  * binary_sensor  <name>_motion      (PIR, device_class MOTION)
  * corrected battery %, plus sensitivity / detection-range / LED config entities.

The quirk registers as soon as this package is imported (HA imports it during
setup). After install + HA restart, re-interview the FP300 once so ZHA rebuilds
it against the now-registered quirk and creates the new entities.
"""

import logging

_LOGGER = logging.getLogger(__name__)

# Importing the module executes its module-level QuirkBuilder(...).add_to_registry(),
# which inserts the FP300 quirk into zigpy's global device registry.
try:
    from . import motion_agl8  # noqa: F401

    _LOGGER.info(
        "Aqara FP300 ZHA quirk registered (Aqara / lumi.sensor_occupy.agl8)"
    )
except Exception:  # pragma: no cover - defensive; surfaced in the HA log
    _LOGGER.exception("Failed to register the Aqara FP300 ZHA quirk")


async def async_setup_entry(hass, entry) -> bool:
    """No runtime work: the quirk is registered at import (above)."""
    return True


async def async_unload_entry(hass, entry) -> bool:
    """Nothing to tear down. The quirk stays registered for the process lifetime."""
    return True
