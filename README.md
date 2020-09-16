# purple-air.py

Python script to help pull Purple-Air sensor data into Home Assistant and then feed the color into an Inovelli light switch.

![Home Assistant Display](https://user-images.githubusercontent.com/622065/93288527-da6ab900-f790-11ea-93f8-092ec9725f9d.png)
![Safe](https://user-images.githubusercontent.com/622065/93288358-89f35b80-f790-11ea-8776-587cdebbf5fc.jpg)
![Unsafe](https://user-images.githubusercontent.com/622065/93288360-8a8bf200-f790-11ea-9a7c-717b7be2bca3.jpg)

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