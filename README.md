# purple-air.py

Python script to help pull Purple-Air sensor data into Home Assistant and then feed the color into an Inovelli light switch.

## Installation

### Sensor Configuration

Following the steps on Home Assistant's [Command-Line Sensor Page](https://www.home-assistant.io/integrations/sensor.command_line/).

```yaml
  - platform: command_line
    name: Purple Air Quality AQI
    json_attributes:
      - pm2.5
      - humidity
      - temp_f
      - pressure
      - aqi
      - name
      - description
      - color
      - colorv
    command: 'python3 /config/scripts/purple-air.py 34871'
    scan_interval: 300
    value_template: '{{ value_json.aqi }}'
    unit_of_measurement: "AQI"
```

### Automation for Inovelli Switch

Following the steps on Home Assistant's [Automation Page](https://www.home-assistant.io/integrations/automation) and using the `zwave.set_config_parameter` service.

In this example, the desired light switch is ZWave node `20`.

```yaml
  - alias: Pollution Detection
    mode: single
    description: ''
    trigger:
    - entity_id: sensor.purple_air_quality_aqi
      platform: state
    condition: []
    action:
    - service: zwave.set_config_parameter
      data_template:
        node_id: '20'
        parameter: '13'
        size: '4'
        value: '{{ state_attr(''sensor.purple_air_quality_aqi'', ''colorv'') }}'
```