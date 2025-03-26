import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID, CONF_NAME
import re

DEPENDENCIES = ["uart"]
AUTO_LOAD = ["binary_sensor"]

c4001_ns = cg.esphome_ns.namespace("c4001")
C4001Sensor = c4001_ns.class_("C4001Sensor", sensor.Sensor, cg.Component, uart.UARTDevice)

CONFIG_SCHEMA = (
    sensor.sensor_schema(
        C4001Sensor,
    )
    .extend(
        {
            cv.GenerateID(): cv.declare_id(C4001Sensor),
            cv.Required(CONF_NAME): cv.string,
        }
    )
    .extend(uart.UARTDevice.UART_DEVICE_SCHEMA.schema)
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await sensor.sensor_to_code(config, var)
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    cg.add(var.set_rx_callback(cg.RawExpression(
        lambda: cg.esphome_ns.runtime.ptr(var).get(),
        "[](C4001Sensor *sensor, const std::vector<uint8_t> &data) {",
        "  std::string received(data.begin(), data.end());",
        "  if (!received.empty()) {",
        "    std::smatch match;",
        "    if (std::regex_search(received, match, std::regex(\"distance: ([0-9.]+)\"))) {",
        "      float distance = std::stof(match[1].str());",
        "      sensor->publish_state(distance);",
        "      sensor->publish_state(distance > 0 ? 1 : 0);",
        "    }",
        "  }",
        "}"
    )))
