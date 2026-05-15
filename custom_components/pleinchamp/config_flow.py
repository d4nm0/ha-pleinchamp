import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_CITY_URL

class PleinchampConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gère le flux de configuration pour Pleinchamp."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Première étape de la configuration via l'interface."""
        errors = {}
        if user_input is not None:
            # Ici on pourrait ajouter une vérification de l'URL si besoin
            return self.async_create_entry(title="Pleinchamp Météo", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_CITY_URL): cv.string,
            }),
            errors=errors,
        )
