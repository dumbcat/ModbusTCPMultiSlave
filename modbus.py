import configparser
import datetime
import logging
import os
from time import sleep

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.constants import Defaults
from pymodbus.exceptions import ConnectionException


def modbus_logger():
    # checking log folder exist or not
    if not os.path.isdir('log/'):
        os.mkdir('log/')

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_name = datetime.datetime.now().strftime("log/tk%Y-%m-%d.log")
    fh = logging.FileHandler(log_name)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)-5s]: %(message)s',
        '%H:%M:%S',
    )
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def modbus_tcp(slave_name, logger, client):
    # result_list save a slave query result
    result_list = []
    # result_dict save all slave query result
    result_dict = {}
    slave_id = config.get(slave_name, 'unit')
    slave_ip = config.get(slave_name, 'ip')
    slave_port = config.get(slave_name, 'port')
    io_types = ['AI', 'AO', 'DI', 'DO', ]

    try:
        print(f"==== {slave_name}({slave_ip}:{slave_port}) "
              f"{datetime.datetime.now().strftime('%H:%M:%S')} ====")
        for io_type in io_types:
            value_dict = {}
            try:
                if config.get(slave_name, f'{io_type.lower()}_enable') == '1':
                    addr = int(config.get(
                        slave_name, f'{io_type.lower()}_address'))
                    count = int(config.get(
                        slave_name, f'{io_type.lower()}_count'))
                    if io_type == 'AI':
                        values = client.read_input_registers(
                            addr, count, unit=int(slave_id))
                        value_dict[io_type] = values.registers
                    elif io_type == 'AO':
                        values = client.read_holding_registers(
                            addr, count, unit=int(slave_id))
                        value_dict[io_type] = values.registers
                    elif io_type == 'DI':
                        values = client.read_discrete_inputs(
                            addr, count, unit=int(slave_id))
                        value_dict[io_type] = values.bits[:count]
                    else:
                        values = client.read_coils(
                            addr, count, unit=int(slave_id))
                        value_dict[io_type] = values.bits[:count]
                    result_list.append(value_dict)
            except AttributeError:
                message = (f"Query {io_type}'s address isn't an allowable value,"
                           f" or {slave_name} was offline.")
                logger.error(message)
        result_dict[slave_name] = result_list

    except ConnectionException:
        message = (f'Fail to connect to {slave_name} in'
                   f' {slave_ip}:{slave_port}')
        logger.error(message)

    return result_dict


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('modbus.ini')

    # Setting Modbus TCP request timeout
    Defaults.Timeout = 1

    logger = modbus_logger()
    slaves = {}

    # Generate ModbusTcpClient objects
    for slave_name in config.sections():
        slaves[slave_name] = ModbusClient(config.get(
            slave_name, 'ip'), config.get(slave_name, 'port'))

    try:
        logger.debug('>>>> START PROGRAM <<<<')
        while True:
            for slave_name in config.sections():
                results = modbus_tcp(slave_name, logger, slaves[slave_name])
                if results:
                    for io_results in results[slave_name]:
                        for io_type in io_results:
                            print(io_type, ':', io_results[io_type])
            sleep(1)
            os.system('cls')
    except KeyboardInterrupt:
        message = '>>>> USER CANCEL PROGRAM <<<<'
        logger.debug(message)
