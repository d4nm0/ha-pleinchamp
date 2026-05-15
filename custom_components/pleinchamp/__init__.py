import logging
from datetime import timedelta
import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_LATITUDE, CONF_LONGITUDE, DEFAULT_SCAN_INTERVAL, USER_AGENT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    lat = entry.data[CONF_LATITUDE]
    lon = entry.data[CONF_LONGITUDE]
    # Construction de l'URL d'API avec les coordonnées
    api_url = f"https://api.prod.pleinchamp.com/forecasts-36h?latitude={lat}&longitude={lon}&page=0"
    
    session = async_get_clientsession(hass)

    async def async_update_data():
        try:
            async with async_timeout.timeout(15):
                headers = {"User-Agent": USER_AGENT}
                response = await session.get(api_url, headers=headers)
                response.raise_for_status()
                json_data = await response.json()

                # Extraction des données
                def get_val(key, index=0):
                    metric = json_data.get(key, [])
                    return metric[index].get("value") if len(metric) > index else 0

                # Calcul Pluie sur 24h (somme des 8 prochaines tranches de 3h)
                precip_24h = sum([get_val("precipitationAmount", i) for i in range(8)])
                
                # Risque de pluie max sur les 8 prochaines tranches
                prob_max = max([get_val("precipitationProbability", i) for i in range(8)])

                weather_code = get_val("weatherCode")
                wind_dir = get_val("windDirection")
                conditions = {2: "Ensoleillé", 3: "Peu nuageux", 15: "Pluie faible", 103: "Nuageux", 115: "Averses"}

                return {
                    "temp": get_val("airTemperature"),
                    "condition": conditions.get(weather_code, f"Code {weather_code}"),
                    "precip": get_val("precipitationAmount"),
                    "precip_24h": round(precip_24h, 2),
                    "prob_max": prob_max,
                    "humidity": get_val("relativeHumidity"),
                    "wind_speed": get_val("windSpeedAt2m"),
                    "wind_dir": wind_dir.get("cardinal") if isinstance(wind_dir, dict) else "N/A",
                    "temp_au_sol": get_val("airTemperatureNearGround"),
                }
        except Exception as err:
            raise UpdateFailed(f"Erreur API Pleinchamp: {err}")

    coordinator = DataUpdateCoordinator(
        hass, _LOGGER, name="Pleinchamp API",
        update_method=async_update_data,
        update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
