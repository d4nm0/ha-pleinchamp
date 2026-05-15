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
        _LOGGER.info("🚀 Tentative de mise à jour Pleinchamp pour l'URL : %s", url)
        try:
            async with async_timeout.timeout(20):
                headers = {"User-Agent": USER_AGENT}
                response = await session.get(url, headers=headers)
                
                if response.status != 200:
                    _LOGGER.error("❌ Erreur HTTP : %s", response.status)
                    raise UpdateFailed(f"Le site a répondu avec le statut {response.status}")

                html = await response.text()
                _LOGGER.debug("HTML reçu (tronqué) : %s", html[:500])
                
                soup = BeautifulSoup(html, 'html.parser')
                data = {}

                # 1. Condition
                cond_block = soup.select_one('[class*="meteo-home-summary-main"] h2')
                data["condition"] = cond_block.text.strip() if cond_block else "Indéterminé"

                # 2. Température
                temp_element = soup.select_one('[class*="meteo-home-summary-temp"]')
                if temp_element:
                    data["temp"] = temp_element.text.replace("°C", "").replace(",", ".").strip()
                else:
                    _LOGGER.warning("⚠️ Impossible de trouver la température actuelle")

                # 3. Les blocs de métriques (Board)
                board = soup.select_one('[class*="metrics-board"]')
                if board:
                    items = board.find_all("div", recursive=False)
                    _LOGGER.info("📊 %s blocs de données trouvés sur la page", len(items))
                    
                    if len(items) >= 5:
                        # Précipitations
                        data["precip"] = items[0].get_text(strip=True).replace("mm", "").replace(",", ".").strip()

                        # Split Min/Max
                        try:
                            min_max_raw = items[1].get_text(strip=True).replace("°C", "")
                            if "/" in min_max_raw:
                                parts = min_max_raw.split("/")
                                data["temp_min"] = parts[0].strip()
                                data["temp_max"] = parts[1].strip()
                            else:
                                data["temp_min"] = data["temp_max"] = min_max_raw.strip()
                        except Exception:
                            _LOGGER.warning("⚠️ Erreur lors du split Min/Max")

                        # Vent, Humidité, Direction
                        data["wind_speed"] = items[2].get_text(strip=True).replace("km/h", "").strip()
                        data["humidity"] = items[3].get_text(strip=True).replace("%", "").strip()
                        data["wind_dir"] = items[4].get_text(strip=True)
                    else:
                        _LOGGER.error("❌ Nombre de blocs insuffisant sur la board")
                else:
                    _LOGGER.error("❌ Impossible de trouver la board 'metrics-board'")

                _LOGGER.info("✅ Mise à jour Pleinchamp terminée avec succès")
                return data

        except Exception as err:
            _LOGGER.error("💥 Erreur lors du scraping Pleinchamp : %s", err)
            raise UpdateFailed(f"Erreur Pleinchamp: {err}")

    # Initialisation du Coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Pleinchamp Sensor",
        update_method=async_update_data,
        update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
    )

    # Premier rafraîchissement
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Déchargement de l'intégration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
