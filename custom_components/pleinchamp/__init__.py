import logging
from datetime import timedelta
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
    
    # URL de l'API avec les coordonnées dynamiques
    api_url = f"https://api.prod.pleinchamp.com/forecasts-36h?latitude={lat}&longitude={lon}&page=0"
    
    session = async_get_clientsession(hass)

    async def async_update_data():
        try:
            async with async_timeout.timeout(15):
                headers = {"User-Agent": USER_AGENT}
                response = await session.get(api_url, headers=headers)
                response.raise_for_status()
                json_data = await response.json()

                # --- FONCTIONS UTILITAIRES ---
                def get_series(key, limit=8):
                    """Récupère une liste de valeurs (par défaut les prochaines 24h / 8 tranches)."""
                    series = json_data.get(key, [])
                    return series[:limit]

                def get_val(key):
                    """Récupère la première valeur disponible (instant T)."""
                    series = json_data.get(key, [])
                    return series[0].get("value") if series else None

                # --- MAPPING ET CALCULS ---
                conditions_map = {2: "Ensoleillé", 3: "Peu nuageux", 15: "Pluie faible", 103: "Nuageux", 115: "Averses"}
                
                # Récupération des séries pour les calculs (24h = 8 tranches de 3h)
                precip_series = get_series("precipitationAmount")
                prob_series = get_series("precipitationProbability")

                # Correction de l'erreur : Somme et Max via compréhension de liste
                precip_24h = sum(item.get("value", 0) for item in precip_series)
                prob_max = max((item.get("value", 0) for item in prob_series), default=0)

                # --- PRÉPARATION DU DICTIONNAIRE DE DONNÉES ---
                return {
                    # Données Instant T
                    "temp": get_val("airTemperature"),
                    "condition": conditions_map.get(get_val("weatherCode"), f"Code {get_val('weatherCode')}"),
                    "precip": get_val("precipitationAmount"),
                    "humidity": get_val("relativeHumidity"),
                    "wind_speed": get_val("windSpeedAt2m"),
                    "wind_dir": get_val("windDirection").get("cardinal") if isinstance(get_val("windDirection"), dict) else "N/A",
                    "temp_au_sol": get_val("airTemperatureNearGround"),
                    
                    # Totaux 24h
                    "precip_24h": round(precip_24h, 2),
                    "prob_max": prob_max,
                    "wind_gust": get_val("maxWindGustAt2m") or 0,
                    "forecast_gust": [item.get("value", 0) for item in get_series("maxWindGustAt2m")],

                    # Séries de prévisions (pour les capteurs Forecast / Graphiques)
                    "forecast_temp": [item.get("value") for item in get_series("airTemperature")],
                    "forecast_precip": [item.get("value") for item in get_series("precipitationAmount")],
                    "forecast_prob": [item.get("value") for item in get_series("precipitationProbability")],
                    "forecast_wind": [item.get("value") for item in get_series("windSpeedAt2m")],
                    "timestamps": [item.get("date") for item in get_series("airTemperature")]
                }
        except Exception as err:
            _LOGGER.error("💥 Erreur lors de la mise à jour Pleinchamp : %s", err)
            raise UpdateFailed(f"Erreur API: {err}")

    # Gestionnaire de mise à jour (Coordinator)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Pleinchamp API",
        update_method=async_update_data,
        update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    
    # Enregistrement de la plateforme sensor
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    """Déchargement de l'entrée de configuration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
