import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_CITY_URL

class PleinchampConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Pleinchamp Météo", data=user_input)

        return self.self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_CITY_URL): str,
            }),
        )