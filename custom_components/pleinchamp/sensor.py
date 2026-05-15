from homeassistant.components.sensor import (
    SensorEntity, 
    SensorDeviceClass, 
    SensorStateClass
)
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des capteurs à partir d'une entrée de configuration."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unique_id = entry.entry_id
    
    # Liste des capteurs à créer
    sensors = [
        PleinchampSensor(coordinator, "Temperature", "temp", "°C", "mdi:thermometer", SensorDeviceClass.TEMPERATURE, unique_id),
        PleinchampSensor(coordinator, "Condition", "condition", None, "mdi:weather-cloudy", None, unique_id),
        PleinchampSensor(coordinator, "Precipitations", "precip", "mm", "mdi:weather-rainy", SensorDeviceClass.PRECIPITATION, unique_id),
        # Nouveaux capteurs
        PleinchampSensor(coordinator, "Pluie 24h", "precip_24h", "mm", "mdi:weather-pouring", SensorDeviceClass.PRECIPITATION, unique_id),
        PleinchampSensor(coordinator, "Risque de pluie", "prob_max", "%", "mdi:water-percent", None, unique_id),
        
        PleinchampSensor(coordinator, "Humidite", "humidity", "%", "mdi:water-percent", SensorDeviceClass.HUMIDITY, unique_id),
        PleinchampSensor(coordinator, "Vent Vitesse", "wind_speed", "km/h", "mdi:wind", SensorDeviceClass.WIND_SPEED, unique_id),
        PleinchampSensor(coordinator, "Vent Direction", "wind_dir", None, "mdi:compass", None, unique_id),
        PleinchampSensor(coordinator, "Temp au sol", "temp_au_sol", "°C", "mdi:snowflake", SensorDeviceClass.TEMPERATURE, unique_id),
    ]
    
    async_add_entities(sensors)

class PleinchampSensor(SensorEntity):
    """Représentation d'un capteur Pleinchamp."""

    def __init__(self, coordinator, name, data_key, unit, icon, device_class, entry_id):
        """Initialisation du capteur."""
        self.coordinator = coordinator
        self._data_key = data_key
        
        # Identification unique de l'entité
        self._attr_name = f"Pleinchamp {name}"
        self._attr_unique_id = f"pleinchamp_{entry_id}_{data_key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = device_class
        
        # Pour avoir des statistiques (graphiques) dans HA
        if device_class in [SensorDeviceClass.TEMPERATURE, SensorDeviceClass.HUMIDITY, SensorDeviceClass.WIND_SPEED]:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Retourne la valeur actuelle depuis le coordinateur."""
        return self.coordinator.data.get(self._data_key)

    @property
    def available(self):
        """Retourne si le capteur est disponible."""
        return self.coordinator.last_update_success

    @property
    def should_poll(self):
        """Pas de rafraîchissement manuel, le coordinateur s'en occupe."""
        return False

    @property
    def device_info(self):
        """Lie l'entité à un appareil unique dans HA."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "Météo Pleinchamp",
            "manufacturer": "Pleinchamp",
            "model": "API Production",
        }

    async def async_added_to_hass(self):
        """S'abonne aux mises à jour du coordinateur."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
