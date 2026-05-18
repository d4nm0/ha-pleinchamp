import logging
from datetime import datetime, timedelta
import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_LATITUDE, CONF_LONGITUDE, DEFAULT_SCAN_INTERVAL, USER_AGENT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    """Configuration de l'intégration via l'API de production."""
    lat = entry.data[CONF_LATITUDE]
    lon = entry.data[CONF_LONGITUDE]
    
    api_url = f"https://api.prod.pleinchamp.com/forecasts-36h?latitude={lat}&longitude={lon}&page=0"
    session = async_get_clientsession(hass)

    async def async_update_data():
        try:
            async with async_timeout.timeout(15):
                headers = {"User-Agent": USER_AGENT}
                response = await session.get(api_url, headers=headers)
                response.raise_for_status()
                json_data = await response.json()

                # --- LOGIQUE DE FILTRAGE TEMPOREL ---
                # On récupère l'heure actuelle au format ISO UTC (ex: 2026-05-18T12:00:00Z)
                # On arrondit à l'heure inférieure pour correspondre aux tranches de l'API
                now_utc = datetime.utcnow()
                current_hour_iso = now_utc.strftime("%Y-%m-%dT%H:00:00Z")

                def get_series(key, limit=8):
                    """Récupère les tranches à partir de maintenant (exclut le passé)."""
                    series = json_data.get(key, [])
                    # On ne garde que ce qui est égal ou futur à l'heure actuelle
                    future_data = [item for item in series if item.get("date") >= current_hour_iso]
                    return future_data[:limit]

                def get_val(key):
                    """Récupère la valeur la plus pertinente pour l'heure actuelle."""
                    series = json_data.get(key, [])
                    if not series:
                        return None
                    
                    # On cherche la correspondance exacte de l'heure
                    for item in series:
                        if item.get("date") == current_hour_iso:
                            return item.get("value")
                    
                    # Si pas de correspondance exacte (ex: entre deux tranches), 
                    # on prend la première valeur qui n'est pas périmée
                    for item in series:
                        if item.get("date") >= current_hour_iso:
                            return item.get("value")
                            
                    return series[0].get("value")

                # --- MAPPING ET CALCULS ---
                conditions_map = {1: "Ensoleillé", 2: "Ensoleillé", 3: "Peu nuageux", 4: "Nuageux", 5: "Très nuageux", 6: "Couvert",
7: "Brouillard", 8: "Ciel couvert / Pluie", 10: "Pluie faible", 11: "Pluie modérée", 12: "Pluie forte",
13: "Pluie faible givrante", 14: "Pluie modérée givrante", 15: "Pluie faible",20: "Faibles averses",
21: "Averses modérées", 22: "Fortes averses", 30: "Neige faible", 31: "Neige modérée", 32: "Neige forte",
40: "Pluie et neige mêlées", 41: "Pluie et neige mêlées", 42: "Pluie et neige mêlées fortes", 60: "Faibles averses de neige",
61: "Averses de neige modérées", 62: "Fortes averses de neige", 70: "Faibles averses de pluie et neige",
71: "Averses de pluie et neige", 72: "Fortes averses de pluie et neige", 80: "Orage faible", 81: "Orage modéré",
82: "Orage fort", 83: "Orage faible avec grêle", 84: "Orage modéré avec grêle", 85: "Orage fort avec grêle",
101: "Nuit claire", 102: "Nuit claire", 103: "Nuageux", 104: "Nuageux", 105: "Très nuageux", 106: "Couvert",
110: "Pluie faible", 111: "Pluie modérée", 112: "Pluie forte", 115: "Averses", 120: "Averses", 121: "Averses modérées", 180: "Orageux"}
                
                precip_series = get_series("precipitationAmount")
                prob_series = get_series("precipitationProbability")

                precip_24h = sum(item.get("value", 0) for item in precip_series)
                prob_max = max((item.get("value", 0) for item in prob_series), default=0)

                return {
                    "temp": get_val("airTemperature"),
                    "condition": conditions_map.get(get_val("weatherCode"), f"Code {get_val('weatherCode')}"),
                    "precip": get_val("precipitationAmount"),
                    "humidity": get_val("relativeHumidity"),
                    "wind_speed": get_val("windSpeedAt2m"),
                    "wind_gust": get_val("maxWindGustAt2m") or 0,
                    "wind_dir": get_val("windDirection").get("cardinal") if isinstance(get_val("windDirection"), dict) else "N/A",
                    "temp_au_sol": get_val("airTemperatureNearGround"),
                    
                    "precip_24h": round(precip_24h, 2),
                    "prob_max": prob_max,

                    "forecast_temp": [item.get("value") for item in get_series("airTemperature")],
                    "forecast_precip": [item.get("value") for item in get_series("precipitationAmount")],
                    "forecast_prob": [item.get("value") for item in get_series("precipitationProbability")],
                    "forecast_wind": [item.get("value") for item in get_series("windSpeedAt2m")],
                    "forecast_gust": [item.get("value") for item in get_series("maxWindGustAt2m")],
                    "timestamps": [item.get("date") for item in get_series("airTemperature")]
                }
        except Exception as err:
            _LOGGER.error("💥 Erreur lors de la mise à jour Pleinchamp : %s", err)
            raise UpdateFailed(f"Erreur API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Pleinchamp API",
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
