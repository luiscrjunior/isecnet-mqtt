from .config import config
import socket
import logging
from enum import Enum
from pydantic import BaseModel

logger = logging.getLogger('alarm')

CMD_PROTOCOL = 0xe9 # 233
CMD_FRAME_DELIMITER = 0x21 # 33
CMD_REQUEST_PARTIAL_STATUS = [0x5b]
CMD_ACTIVATE_CENTRAL = [0x41]
CMD_DEACTIVATE_CENTRAL = [0x44]
CMD_ACTIVATE_PARTITION_A = [0x41, 0x41]
CMD_DEACTIVATE_PARTITION_A = [0x44, 0x41]
CMD_ACTIVATE_PARTITION_B = [0x41, 0x42]
CMD_DEACTIVATE_PARTITION_B = [0x44, 0x42]

class AlarmCentralPartialStatus(BaseModel):
    siren_triggered: bool = False
    partition_A: bool = False
    partition_B: bool = False
    partition_C: bool = False
    partition_D: bool = False

def _int_to_binary(number: int) -> str:
    return '{0:08b}'.format(number)

def _checksum(command: list[int]) -> int:
    i = 0
    for command_item in command:
        i = i ^ command_item
    return i ^ 255

def _generate_data_frame(command: list[int]) -> list[int]:
    frame = []
    frame.append(len(command) + len(config.alarm_passwd) + 3)
    frame.append(CMD_PROTOCOL)
    frame.append(CMD_FRAME_DELIMITER)
    for password_char in str(config.alarm_passwd):
        frame.append(ord(password_char))
    frame = frame + command
    frame.append(CMD_FRAME_DELIMITER)
    frame.append(_checksum(frame))
    return frame

def _pretty(command: list[int]) -> str:
    return "[" + ",".join(map(hex,command)) + "]"

def _send_alarm_cmd(command: list[int]) -> None or list[int]:
    frame = _generate_data_frame(command)
    logger.debug("Conectando com a central...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.alarm_addr, config.alarm_port))
    logger.debug("Conexão realizada com sucesso.")
    response = None
    s.send(bytes(frame))
    logger.debug("Enviando comando para a central: " + _pretty(frame))
    response = s.recv(1024)
    s.close()
    if response:
        response_command = list(response)
        logger.debug("Recebida resposta da central: " + _pretty(response_command))
        return response_command
    else:
        return None
        
def request_partial_status() -> AlarmCentralPartialStatus:
    response = _send_alarm_cmd(CMD_REQUEST_PARTIAL_STATUS)
    if response is None:
        raise Exception("Recebida resposta inválida da Central.")
    #TODO: Checar o código de resposta se sucesso
    alarm_status = AlarmCentralPartialStatus()
    alarm_status.partition_A = True if _int_to_binary(response[29])[7] == '1' else False
    alarm_status.partition_B = True if _int_to_binary(response[29])[6] == '1' else False
    alarm_status.partition_C = True if _int_to_binary(response[30])[7] == '1' else False
    alarm_status.partition_D = True if _int_to_binary(response[30])[6] == '1' else False
    alarm_status.siren_triggered = True if _int_to_binary(response[47])[4] == '1' else False
    return alarm_status

def activate_partition_A():
    _send_alarm_cmd(CMD_ACTIVATE_PARTITION_A)

def deactivate_partition_A():
    _send_alarm_cmd(CMD_DEACTIVATE_PARTITION_A)

def activate_partition_B():
    _send_alarm_cmd(CMD_ACTIVATE_PARTITION_B)

def deactivate_partition_B():
    _send_alarm_cmd(CMD_DEACTIVATE_PARTITION_B)
