import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, uart
from esphome.const import CONF_ID, CONF_NAME

DEPENDENCIES = ["uart"]
AUTO_LOAD = ["binary_sensor"]

c4001_ns = cg.esphome_ns.namespace("c4001")
C4001Sensor = c4001_ns.class_("C4001Sensor", sensor.Sensor, cg.Component, uart.UARTDevice)

CONFIG_SCHEMA = (
    sensor.sensor_schema(C4001Sensor)
    .extend(
        {
            cv.GenerateID(): cv.declare_id(C4001Sensor),
            cv.Required(CONF_NAME): cv.string,
        }
    )
    .extend(uart.UART_DEVICE_SCHEMA)
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_sensor(var, config)  # ✅ Correct function
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    # ✅ Fix: Properly register a callback function
    cg.add(var.set_rx_callback(cg.lambda_("const std::vector<uint8_t> &data", """
        std::string received(data.begin(), data.end());
        if (!received.empty()) {
            size_t pos = received.find("distance: ");
            if (pos != std::string::npos) {
                std::string value_str = received.substr(pos + 9);
                float distance = std::stof(value_str);
                obj->publish_state(distance);
            }
        }
    """)))
