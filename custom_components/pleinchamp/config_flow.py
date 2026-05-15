import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_LATITUDE, CONF_LONGITUDE

class PleinchampConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestion du formulaire de configuration."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=f"Météo ({user_input[CONF_LATITUDE]}, {user_input[CONF_LONGITUDE]})", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_LATITUDE): str,
                vol.Required(CONF_LONGITUDE): str,
            }),
        )
