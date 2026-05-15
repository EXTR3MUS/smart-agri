from pyModbusTCP.client import ModbusClient

c = ModbusClient(host='localhost', port=5020, auto_open=True)


print("Leitura de dados MODBUS")
regs = c.read_input_registers(0, 2)
if regs:
    print(f"Temperatura: {regs[0]/10}°C")
    print(f"Umidade Solo: {regs[1]}%")


# Atualizar setpoint de umidade
if(1):
    if c.write_single_register(1, 20):
        print("Escrita realizada com sucesso (FC 06)")


# Mudar modo (Automático/Manual)
c.write_single_register(0, 0) # 0 - Modo Manual
# c.write_single_register(0, 1) # 1 - Modo Automático


c.write_single_coil(1, True)  # Liga Exaustor (FC 05)

c.close()