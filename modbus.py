import os
import logging
import datetime
import configparser
from time import sleep
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.exceptions import ConnectionException
from pymodbus.constants import Defaults

# checking log folder exist or not
if not os.path.isdir('log/'):
    os.mkdir('log/')

# setting logging to file
log_filename = datetime.datetime.now().strftime("log/tk%Y-%m-%d.log")
hdlr = logging.FileHandler(log_filename)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)-5s] %(name)-10s %(message)s',
    '%H:%M:%S',
)
hdlr.setFormatter(formatter)
hdlr.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(hdlr)

# Read modbus.ini
config = configparser.ConfigParser()
config.read('modbus.ini')

# Setting Modbus TCP request timeout
Defaults.Timeout = 1

# Create dynamic variable by sections numbers
# eg. client1, client2,client3...etc.
for i in range(len(config.sections())):
    slave_name = 'SLAVE ' + str(i + 1)
    address = config.get(slave_name, 'ip_address')
    port = config.get(slave_name, 'port')
    globals()['client%s' % str(i + 1)] = ModbusClient(address, port)


# Read Modbus TCP valus according to configuration file
def modbus_tcp():

    result_dict = {}

    for i in range(len(config.sections())):
        client = globals()['client%s' % str(i + 1)]
        slave_name = 'SLAVE ' + str(i + 1)
        slave_id = config.get(slave_name, 'unit')
        result_list = []

        # Read multi-input registers (3xxxx), for AI
        # read_input_registers(start_addr, count, unit=sid)
        try:
            if config.get(slave_name, 'ai_enable') == '1':
                ai_addr = int(config.get(slave_name, 'ai_address'))
                ai_count = int(config.get(slave_name, 'ai_count'))
                ais = client.read_input_registers(
                    ai_addr, ai_count, unit=int(slave_id))
                value_dict = {'AIs': ais.registers}
                result_list.append(value_dict)

            # Read multi-registers (4xxxx) for AO
            # read_holding_registers(start_addr, count, unit=sid)
            if config.get(slave_name, 'ao_enable') == '1':
                ao_addr = int(config.get(slave_name, 'ao_address'))
                ao_count = int(config.get(slave_name, 'ao_count'))
                aos = client.read_holding_registers(
                    ao_addr, ao_count, unit=int(slave_id))
                value_dict = {'AOs': aos.registers}
                result_list.append(value_dict)

            # Read multi-input discrete ( 1xxxx ) for DI
            # read_discrete_inputs(start_addr, bit count, unit=sid)
            # will reply 1 byte --> 8 bits
            if config.get(slave_name, 'di_enable') == '1':
                di_addr = int(config.get(slave_name, 'di_address'))
                di_count = int(config.get(slave_name, 'di_count'))
                dis = client.read_discrete_inputs(
                    di_addr, di_count, unit=int(slave_id))
                value_dict = {'DIs': dis.bits[:di_count]}
                result_list.append(value_dict)

            # Read multi-coils status (0xxxx) for DO
            # read_coils(start_addr, bit count, unit=sid)
            # will reply 1 byte --> 8 bits
            if config.get(slave_name, 'do_enable') == '1':
                do_addr = int(config.get(slave_name, 'do_address'))
                do_count = int(config.get(slave_name, 'do_count'))
                dos = client.read_coils(
                    do_addr, do_count, unit=int(slave_id))
                value_dict = {'DOs': dos.bits[:do_count]}
                result_list.append(value_dict)

            result_list.append(
                {'time': datetime.datetime.now().strftime("%H:%M:%S")})
            result_dict[slave_name] = result_list
        except ConnectionException:
            message = 'Fail to connect to modbus slave ' + \
                address + ':' + port
            logger.error(message)
        except AttributeError:
            message = "Query address isn't an allowable value, " + \
                'or slave was offline.'
            logger.error(message)
        except KeyboardInterrupt:
            message = 'User cancel program.'
            logger.debug(message)
    return result_dict
    # client.close()


if __name__ == '__main__':
    while True:
        result = modbus_tcp()
        print(result)
        os.system('cls')
        for key in result:  # key = section of config
            slave_ip = config.get(key, 'ip_address')
            slave_port = config.get(key, 'port')
            print('====[%s] %15s:%-5s====' % (key, slave_ip, slave_port))
            for i in result[key]:
                for key in i:
                    print(key, ':', i[key])
        sleep(1)
