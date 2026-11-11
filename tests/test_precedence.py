"""Precedence tests against the HA 2026.11 ZHA stack (zha==2.4.2, zha-quirks==2.4.1).

Each case runs in a fresh interpreter because quirk registration is a
process-global import side effect.
    python -m unittest discover -s tests
"""
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OURS = "custom_components.aqara_fp300_quirk.motion_agl8"
UPSTREAM = "zhaquirks.xiaomi.aqara.motion_agl8"

PROBE = r"""
import importlib, sys
sys.path.insert(0, {root!r})
from zha.quirks import DEVICE_REGISTRY, ModelInfo
import zhaquirks
if {ours_first!r}:
    importlib.import_module("custom_components.aqara_fp300_quirk")
    zhaquirks.setup()
else:
    zhaquirks.setup()
    importlib.import_module("custom_components.aqara_fp300_quirk")
zhaquirks.setup()  # a second walk (e.g. ZHA reload) must not bring the basic quirk back
ents = DEVICE_REGISTRY._registry[ModelInfo("Aqara", "lumi.sensor_occupy.agl8")]
print("|".join(e.source.module for e in ents))
print(len(ents[0].zha_device_factory.quirk_definition.entity_metadata))
"""


def probe(ours_first):
    out = subprocess.run(
        [sys.executable, "-W", "ignore", "-c", PROBE.format(root=ROOT, ours_first=ours_first)],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return out[0].split("|"), int(out[1])


class Precedence(unittest.TestCase):
    def test_ours_wins_when_loaded_before_zha_walk(self):
        # This is the production order on HA 2026.11 (the bug: basic quirk won).
        mods, n = probe(True)
        self.assertEqual(mods[0], OURS)
        self.assertNotIn(UPSTREAM, mods)
        self.assertGreater(n, 30)

    def test_ours_wins_when_loaded_after_zha_walk(self):
        mods, n = probe(False)
        self.assertEqual(mods[0], OURS)
        self.assertNotIn(UPSTREAM, mods)
        self.assertGreater(n, 30)

    def test_only_one_fp300_entry(self):
        mods, _ = probe(True)
        self.assertEqual(mods, [OURS])


if __name__ == "__main__":
    unittest.main()