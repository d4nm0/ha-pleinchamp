import logging
from datetime import timedelta
import async_timeout
from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_CITY_URL, DEFAULT_SCAN_INTERVAL, USER_AGENT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    """Configuration de l'intégration via l'UI."""
    url = entry.data[CONF_CITY_URL]
    session = async_get_clientsession(hass)

    async def async_update_data():
        try:
            async with async_timeout.timeout(15):
                headers = {"User-Agent": USER_AGENT}
                response = await session.get(url, headers=headers)
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                data = {}

                # 1. Condition (On essaie de trouver le texte court)
                cond_block = soup.select_one('[class*="meteo-home-summary-main"] h2')
                data["condition"] = cond_block.text.strip() if cond_block else "Indéterminé"

                # 2. Température (on enlève le °C pour n'avoir que le nombre)
                temp_element = soup.select_one('[class*="meteo-home-summary-temp"]')
                if temp_element:
                    data["temp"] = temp_element.text.replace("°C", "").replace(",", ".").strip()

                # 3. Les blocs de métriques
                board = soup.select_one('[class*="metrics-board"]')
                if board:
                    items = board.find_all("div", recursive=False)
                    # Ordre : Pluie, MinMax, Vent, Humidité, Direction
                    data["precip"] = items[0].get_text(strip=True).replace("mm", "").replace(",", ".").strip()

                    # Split Min/Max
                    min_max = items[1].get_text(strip=True).replace("°C", "").split("/")
                    data["temp_min"] = min_max[0].strip()
                    data["temp_max"] = min_max[1].strip()

                    data["wind_speed"] = items[2].get_text(strip=True).replace("km/h", "").strip()
                    data["humidity"] = items[3].get_text(strip=True).replace("%", "").strip()
                    data["wind_dir"] = items[4].get_text(strip=True)

                return data
        except Exception as err:
            _LOGGER.error("Erreur lors du scraping Pleinchamp: %s", err)
            raise UpdateFailed(f"Erreur Pleinchamp: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Pleinchamp Sensor",
        update_method=async_update_data,
        update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True