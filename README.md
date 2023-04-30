# isecnet-mqtt

Pequena aplicação escrita em python que se comunica com a central de Alarme Intelbras AMT4010 Smart e envia periodicamente uma mensagem com o status para um tópico no servidor MQTT.

Também escuta um outro tópico para receber comandos.

Foi desenvolvida para integrar a central com o Home Assistant:

![image](https://user-images.githubusercontent.com/13292515/235346988-90c94ed3-2652-49b6-8099-e911d9931f56.png)

## Funcionalidades

Envia o status das partições A, B, C e D e se a sirene está ativada.

Mensagem de status:
```json
{"siren_triggered": false, "partition_A": false, "partition_B": false, "partition_C": false, "partition_D": false}
```

Recebe os comandos:
- ACTIVATE_PARTITION_A
- DEACTIVATE_PARTITION_A
- ACTIVATE_PARTITION_B
- DEACTIVATE_PARTITION_B

Essa é uma primeira versão, bem básica. Outras funcionalidades/comandos podem ser incorporadas (ler zonas, pgms etc).

## Instalação

Faça um git clone desse repositório `git clone https://github.com/luiscrjunior/isecnet-mqtt.git` e crie um arquivo `config.yml` na raiz do projeto. Use como modelo o `config.example.yml`.

```yaml
#IP da Central de Alarme
alarm_addr: 192.168.x.x

#Porta da Central de Alarme (padrão: 9009)
alarm_port: 9009

#Senha da Central de Alarme
alarm_passwd: 1234

#IP/Host do servidor MQTT
mqtt_addr: 192.168.x.x

#Porta do servidor MQTT
mqtt_port: 1883

#Usuário MQTT
mqtt_user: usuario

#Senha MQTT
mqtt_passwd: senha

#De quanto em quanto tempo o status da central vai ser enviado (em segundos)
send_status_interval: 10

#Tópico MQTT que a mensagem de status do alarme será enviado
mqtt_topic_alarm_status: "alarm/status"

#Tópico MQTT para escutar os controles
mqtt_topic_alarm_control: "alarm/control"
```

Instale as dependências com `pip install -r requirements.txt` e depois execute a aplicação com `python app.py`

Versão python >= 3.11.
