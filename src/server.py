from pyModbusTCP.server import ModbusServer, DataBank
import time

from environment import EnvironmentSimulator
from config import (
    SERVER_HOST,
    SERVER_PORT,
    DAY_DURATION_SECONDS,
    MIN_TEMP,
    MAX_TEMP,
    INITIAL_SOIL_MOISTURE,
    DAILY_MOISTURE_DECAY,
    DAILY_IRRIGATION_GAIN,
    INITIAL_MODE,
    INITIAL_SETPOINT,
    LOG_INTERVAL_SECONDS,
)

# Address (Base 0)
# Modbus 30001 -> Address 0 (Input Register)
# Modbus 00001 -> Address 0 (Coil)
# Modbus 40001 -> Address 0 (Holding Register)

ADDR_TEMP = 0        # 30001
ADDR_SOIL = 1        # 30002
ADDR_PUMP = 0        # 00001
ADDR_FAN  = 1        # 00002
ADDR_MODE = 0        # 40001
ADDR_SETPOINT = 1    # 40002

class GreenhouseServer:
    def __init__(self, host=None, port=None, day_duration_seconds=None):
        host = host or SERVER_HOST
        port = port or SERVER_PORT
        day_duration_seconds = day_duration_seconds or DAY_DURATION_SECONDS

        self.db = DataBank()
        self.server = ModbusServer(host=host, port=port, no_block=True, data_bank=self.db)
        self.simulator = EnvironmentSimulator(
            day_duration_seconds=day_duration_seconds,
            min_temp=MIN_TEMP,
            max_temp=MAX_TEMP,
            initial_soil_moisture=INITIAL_SOIL_MOISTURE,
            daily_moisture_decay=DAILY_MOISTURE_DECAY,
            daily_irrigation_gain=DAILY_IRRIGATION_GAIN,
        )

        self.db.set_holding_registers(ADDR_MODE, [INITIAL_MODE])
        self.db.set_holding_registers(ADDR_SETPOINT, [INITIAL_SETPOINT])
        self.db.set_input_registers(ADDR_SOIL, [int(INITIAL_SOIL_MOISTURE)])
        self.db.set_coils(ADDR_PUMP, [False])
        self.db.set_coils(ADDR_FAN, [False])
        
    def run(self):
        print(f"Servidor Modbus TCP Iniciado em {self.server.host}:{self.server.port}")
        self.server.start()
        
        previous_time = time.time()
        try:
            while True:
                current_time = time.time()
                elapsed = current_time - previous_time
                previous_time = current_time

                mode = self.db.get_holding_registers(ADDR_MODE)[0]
                setpoint = self.db.get_holding_registers(ADDR_SETPOINT)[0]
                pump_on = self.db.get_coils(ADDR_PUMP)[0]

                temp, soil = self.simulator.update(pump_on=pump_on, elapsed_seconds=elapsed)
                self.db.set_input_registers(ADDR_TEMP, [temp])

                if mode == 1:  # AUTO mode
                    if soil < setpoint:
                        self.db.set_coils(ADDR_PUMP, [True])
                        pump_on = True
                    else:
                        self.db.set_coils(ADDR_PUMP, [False])
                        pump_on = False

                self.db.set_input_registers(ADDR_SOIL, [soil])

                fan_on = self.db.get_coils(ADDR_FAN)[0]
                fan_status = "LIGADO" if fan_on else "DESLIGADO"

                pump_status = "LIGADA" if pump_on else "DESLIGADA"
                day_progress = (self.simulator.simulation_time % self.simulator.day_duration_seconds) / self.simulator.day_duration_seconds
                period = "Dia" if day_progress < 0.5 else "Noite"
                simulated_time = self.simulator.get_simulated_time()

                print(
                    f"Temp: {temp/10:5.1f}°C | "
                    f"Solo: {soil:3d}% | "
                    f"Modo: {('Auto' if mode == 1 else 'Man'):<4} | "
                    f"Bomba: {pump_status:<8} | "
                    f"Exaustor: {fan_status:<8} | "
                    f"Ciclo: {period} ({simulated_time} / {day_progress*100:3.0f}%)"
                )

                time.sleep(LOG_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            self.server.stop()
            print("Servidor encerrado.")

if __name__ == "__main__":
    GreenhouseServer(day_duration_seconds=DAY_DURATION_SECONDS).run()