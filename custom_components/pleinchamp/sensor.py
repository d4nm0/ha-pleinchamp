from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    uid = entry.entry_id
    
    sensors = []

    # 1. Capteurs Instantanés (Temps Réel)
    sensors.append(PleinchampSensor(coordinator, "Temperature", "temp", "°C", "mdi:thermometer", SensorDeviceClass.TEMPERATURE, uid))
    sensors.append(PleinchampSensor(coordinator, "Condition", "condition", None, "mdi:weather-cloudy", None, uid))
    sensors.append(PleinchampSensor(coordinator, "Precipitations", "precip", "mm", "mdi:weather-rainy", SensorDeviceClass.PRECIPITATION, uid))
    sensors.append(PleinchampSensor(coordinator, "Humidite", "humidity", "%", "mdi:water-percent", SensorDeviceClass.HUMIDITY, uid))
    sensors.append(PleinchampSensor(coordinator, "Vent Vitesse", "wind_speed", "km/h", "mdi:wind", SensorDeviceClass.WIND_SPEED, uid))
    sensors.append(PleinchampSensor(coordinator, "Vent Direction", "wind_dir", None, "mdi:compass", None, uid))
    sensors.append(PleinchampSensor(coordinator, "Temp au sol", "temp_au_sol", "°C", "mdi:snowflake", SensorDeviceClass.TEMPERATURE, uid))
    # --- AJOUT DES RAFALES ---
    sensors.append(PleinchampSensor(coordinator, "Rafales Vent", "wind_gust", "km/h", "mdi:weather-windy-variant", SensorDeviceClass.WIND_SPEED, uid))

    # 2. Capteurs de Cumul / Max (24h)
    sensors.append(PleinchampSensor(coordinator, "Pluie 24h", "precip_24h", "mm", "mdi:weather-pouring", SensorDeviceClass.PRECIPITATION, uid))
    sensors.append(PleinchampSensor(coordinator, "Risque de pluie", "prob_max", "%", "mdi:water-percent", None, uid))

    # 3. Capteurs de Prévisions (Séries pour graphiques)
    sensors.append(PleinchampForecastSensor(coordinator, "Previsions Temperature", "forecast_temp", "°C", "mdi:chart-line", uid))
    sensors.append(PleinchampForecastSensor(coordinator, "Previsions Pluie", "forecast_precip", "mm", "mdi:chart-bell-curve", uid))
    # --- AJOUT PRÉVISIONS RAFALES ---
    sensors.append(PleinchampForecastSensor(coordinator, "Previsions Rafales", "forecast_gust", "km/h", "mdi:weather-windy", uid))

    async_add_entities(sensors)

class PleinchampSensor(SensorEntity):
    def __init__(self, coordinator, name, data_key, unit, icon, device_class, entry_id):
        self.coordinator = coordinator
        self._data_key = data_key
        self._attr_name = name
        self._attr_unique_id = f"pleinchamp_{entry_id}_{data_key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_device_class = device_class
        if device_class:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self): return self.coordinator.data.get(self._data_key)
    @property
    def device_info(self): return {"identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)}, "name": "Météo Pleinchamp"}
    @property
    def available(self): return self.coordinator.last_update_success
    @property
    def should_poll(self): return False
    async def async_added_to_hass(self): self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

class PleinchampForecastSensor(SensorEntity):
    def __init__(self, coordinator, name, data_key, unit, icon, entry_id):
        self.coordinator = coordinator
        self._data_key = data_key
        self._attr_name = name
        self._attr_unique_id = f"pleinchamp_{entry_id}_{data_key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon

    @property
    def native_value(self):
        series = self.coordinator.data.get(self._data_key, [])
        return series[0] if series else None

    @property
    def extra_state_attributes(self):
        return {
            "data": self.coordinator.data.get(self._data_key),
            "timestamps": self.coordinator.data.get("timestamps")
        }

    @property
    def device_info(self): return {"identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)}, "name": "Météo Pleinchamp"}
    @property
    def available(self): return self.coordinator.last_update_success
    async def async_added_to_hass(self): self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
