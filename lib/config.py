import yaml
from pydantic import BaseModel

class Configuration(BaseModel):
    alarm_addr: str
    alarm_port: int
    alarm_passwd: str
    mqtt_addr: str
    mqtt_port: int
    mqtt_user: str
    mqtt_passwd: str
    send_status_interval: int
    mqtt_topic_alarm_status: str
    mqtt_topic_alarm_control: str

config = None

with open('./config.yml', 'r') as file:
    config_dict = yaml.safe_load(file)
    config = Configuration(**config_dict)