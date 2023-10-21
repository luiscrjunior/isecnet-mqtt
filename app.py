import sys
from paho.mqtt import client as mqtt
import json
import schedule
import logging
import time
from lib.config import config
from lib import alarm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("alarm")


def mqtt_send_alarm_status(client: mqtt.Client):
    logger.info("Enviando status da Central para o servidor MQTT...")
    alarm_status = None
    try:
        alarm_status = alarm.request_partial_status()
    except Exception as err:
        logger.error("Erro ao requisitar o status da Central")
        logger.exception(err)
        return
    try:
        payload = json.dumps(alarm_status.dict())
        response = client.publish(config.mqtt_topic_alarm_status, payload)
        response.wait_for_publish()
        if response.is_published():
            logger.info(
                "Status enviado para o tópico '%s': %s"
                % (config.mqtt_topic_alarm_status, payload)
            )
    except Exception as err:
        logger.error("Não foi possível enviar o status para o MQTT")
        logger.exception(err)


def mqtt_handle_message(client, userdata, message):
    cmd = None
    try:
        cmd = str(message.payload.decode("utf-8", "ignore"))
    except Exception as err:
        logger.error("Erro ao codificar mensagem do MQTT.")
        logger.exception(err)
        return
    logger.info(
        "Recebida mensagem no tópico '%s': %s" % (config.mqtt_topic_alarm_control, cmd)
    )
    try:
        if cmd == "ACTIVATE_ALARM":
            alarm.activate_alarm()
        elif cmd == "DEACTIVATE_ALARM":
            alarm.deactivate_alarm()
        elif cmd == "ACTIVATE_PARTITION_A":
            alarm.activate_partition_A()
        elif cmd == "DEACTIVATE_PARTITION_A":
            alarm.deactivate_partition_A()
        elif cmd == "ACTIVATE_PARTITION_B":
            alarm.activate_partition_B()
        elif cmd == "DEACTIVATE_PARTITION_B":
            alarm.deactivate_partition_B()
        elif cmd == "ACTIVATE_PARTITION_C":
            alarm.activate_partition_C()
        elif cmd == "DEACTIVATE_PARTITION_C":
            alarm.deactivate_partition_C()
        elif cmd == "ACTIVATE_PARTITION_D":
            alarm.activate_partition_D()
        elif cmd == "DEACTIVATE_PARTITION_D":
            alarm.deactivate_partition_D()
    except Exception as err:
        logger.error("Erro ao executar o comando %s na central." % (cmd))
        logger.exception(err)
        return


logger.info("Iniciando...")

logger.info("Estabelecendo conexão com o servidor MQTT...")
client = None


def mqtt_on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("[MQTT] Conectado.")
        client.subscribe(config.mqtt_topic_alarm_control)
    else:
        logger.info("[MQTT] Erro ao se conectar com o servidor.")


def mqtt_on_disconnect(client, userdata, rc):
    logger.info("[MQTT] Cliente desconectado.")
    try:
        logger.info("[MQTT] Tentando reconectar...")
        client.connect(
            config.mqtt_addr,
            port=config.mqtt_port,
        )
    except:
        logger.info("[MQTT] Erro ao se reconectar com o servidor.")


try:
    client = mqtt.Client()
    client.on_message = mqtt_handle_message
    client.on_connect = mqtt_on_connect
    client.on_disconnect = mqtt_on_disconnect
    client.username_pw_set(config.mqtt_user, password=config.mqtt_passwd)
    client.connect(
        config.mqtt_addr,
        port=config.mqtt_port,
    )
    client.loop(timeout=1.0, max_packets=1)
    if client.is_connected() == False:
        raise Exception("Não foi possível se conectar com o servidor MQTT.")
except Exception as err:
    logger.error("Erro na conexão com o servidor MQTT.")
    logger.exception(err)
    sys.exit()

logger.info("Conexão MQTT OK.")
client.loop_start()

mqtt_send_alarm_status(client)
schedule.every(config.send_status_interval).seconds.do(mqtt_send_alarm_status, client)

while True:
    schedule.run_pending()
    time.sleep(1)
