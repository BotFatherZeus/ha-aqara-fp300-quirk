"""Single-instance config flow for the Aqara FP300 quirk loader.

There is nothing to configure — adding the entry simply keeps the integration
loaded so its quirk stays registered across restarts. Importing this module's
parent package (which happens when HA loads the config flow) is what registers
the quirk.
"""

from homeassistant.config_entries import ConfigFlow

DOMAIN = "aqara_fp300_quirk"


class AqaraFP300QuirkConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add the FP300 quirk loader (no user input required)."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Create the single entry, refusing duplicates."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Aqara FP300 ZHA Quirk", data={})
