#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/time.h>

#include "ohos_init.h"
#include "cmsis_os2.h"
#include "wifi_connect.h"
#include "MQTTClient.h"
#include "wifiiot_pwm.h"
#include "wifiiot_errno.h"
#include "wifiiot_gpio.h"
#include "wifiiot_gpio_ex.h"
#include "wifiiot_uart.h"


// 串口配置
#define UART_TASK_STACK_SIZE 1024 * 8
#define UART_TASK_PRIO 25
#define UART_BUFF_SIZE 1000
char *uart_data = "helloworld";
uint8_t *uart_buff_ptr;

// MQTT配置
#define EXAMPLE_PRODUCT_KEY "k1a2tFPAdd6"
#define EXAMPLE_DEVICE_NAME "Hi3861Bearpi"
#define EXAMPLE_DEVICE_SECRET "d360367ceca4f87be359e7974460c81c"

char* host = "k1a2tFPAdd6.iot-as-mqtt.cn-shanghai.aliyuncs.com";
char* clientId = "k1a2tFPAdd6.Hi3861Bearpi|securemode=2,signmethod=hmacsha256,timestamp=1715862560386|";
char* username = "Hi3861Bearpi&k1a2tFPAdd6";
char* password = "c673c3f8267c96b9964644c8cc4d53bf5bb6f862bf8dab06ade07929569a1d69";

volatile int toStop = 0;
Network network;
static unsigned char sendBuf[1000];
static unsigned char readBuf[1000];

void cfinish(int sig)
{
    signal(SIGINT, NULL);
    printf("不使用就报错%d\n", sig);
    toStop = 1;
}

void messageArrived(MessageData* md)
{
    MQTTMessage* message = md->message;
    printf("%.*s\t", md->topicName->lenstring.len, md->topicName->lenstring.data);
    printf("%.*s\n", (int)message->payloadlen, (char*)message->payload);
}

int mqtt_example(void)
{
    int rc = 0;

    // 设置缓冲区
    unsigned char buf[1000];
    unsigned char readbuf[1000];

    Network n;
    MQTTClient c;
    char* host = "k1a2tFPAdd6.iot-as-mqtt.cn-shanghai.aliyuncs.com";
    short port = 1883;

    const char* subTopic = "/" EXAMPLE_PRODUCT_KEY "/" EXAMPLE_DEVICE_NAME "/user/get";
    const char* pubTopic = "/" EXAMPLE_PRODUCT_KEY "/" EXAMPLE_DEVICE_NAME "/user/update";

    printf("clientId: %s\n", clientId);
    printf("username: %s\n", username);
    printf("password: %s\n", password);

    signal(SIGINT, cfinish);
    signal(SIGTERM, cfinish);

    // 网络初始化并建立连接
    NetworkInit(&n);
    rc = NetworkConnect(&n, host, port);
    printf("NetworkConnect %d\n", rc);

    // 初始化MQTT客户端
    MQTTClientInit(&c, &n, 1000, buf, sizeof(buf), readbuf, sizeof(readbuf));
    c.defaultMessageHandler = messageArrived;

    // 设置MQTT连接参数
    MQTTPacket_connectData data = MQTTPacket_connectData_initializer;       
    data.willFlag = 0;
    data.MQTTVersion = 3;
    data.clientID.cstring = clientId;
    data.username.cstring = username;
    data.password.cstring = password;
    data.keepAliveInterval = 60;
    data.cleansession = 1;
    printf("Connecting to %s %d\n", host, port);

    rc = MQTTConnect(&c, &data);
    if (rc != 0) {
        printf("MQTTConnect: %d\n", rc);
        return -1;
    }
    printf("MQTTConnect %d, Connect aliyun IoT Cloud Success!\n", rc);
    
    printf("Subscribing to %s\n", subTopic);
    rc = MQTTSubscribe(&c, subTopic, 1, messageArrived);
    printf("MQTTSubscribe %d\n", rc);

    int cnt = 0;
    unsigned int msgid = 0;
    while (!toStop)
    {
        MQTTYield(&c, 1000);    

        if (++cnt % 5 == 0) {
            MQTTMessage msg = {
                QOS1, 
                0,
                0,
                0,
                "Hello world",
                strlen("Hello world"),
            };
            msg.id = ++msgid;
            rc = MQTTPublish(&c, pubTopic, &msg);
            printf("MQTTPublish %d, msgid %d\n", rc, msgid);
            if (rc != 0) {
                printf("Return code from MQTT publish is %d\n", rc);
                NetworkDisconnect(&n);
                MQTTDisconnect(&c);
                osDelay(200);
                return -1;
            }
        }
    }

    printf("Stopping\n");

    MQTTDisconnect(&c);
    NetworkDisconnect(&n);

    return 0;
}

static void MQTT_DemoTask(void)
{
    WifiConnect("sha", "12345678");
    printf("Starting ...\n");
    int rc, count = 0;
    MQTTClient client;

    NetworkInit(&network);
    printf("NetworkConnect  ...\n");
begin:
    rc = NetworkConnect(&network, host, 1883);
    printf("NetworkConnect: %d\n", rc);
    if (rc != 0) {
        printf("Failed to connect to network, retrying...\n");
        osDelay(200);
        goto begin;
    }

    printf("MQTTClientInit  ...\n");
    MQTTClientInit(&client, &network, 2000, sendBuf, sizeof(sendBuf), readBuf, sizeof(readBuf));

    MQTTString clientIdString = MQTTString_initializer;
    clientIdString.cstring = clientId;

    MQTTPacket_connectData data = MQTTPacket_connectData_initializer;
    data.clientID = clientIdString;
    data.willFlag = 0;
    data.MQTTVersion = 3;
    data.keepAliveInterval = 60;
    data.cleansession = 1;
    data.username.cstring = username;
    data.password.cstring = password;

    printf("MQTTConnect  ...\n");
    rc = MQTTConnect(&client, &data);
    printf("MQTTConnectDemo: %d\n", rc);
    if (rc != 0) {
        printf("MQTTConnectDemo failed, return code: %d\n", rc);
        NetworkDisconnect(&network);
        MQTTDisconnect(&client);
        osDelay(200);
        goto begin;
    }

    printf("MQTTSubscribe  ...\n");
    rc = MQTTSubscribe(&client, "substopic", 2, messageArrived);
    printf("MQTTSubscribe: %d\n", rc);
    if (rc != 0) {
        printf("MQTTSubscribe failed, return code: %d\n", rc);
        osDelay(200);
        goto begin;
    }
    
    while (++count)
    {
        const char* pub_topic = "/k1a2tFPAdd6/Hi3861Bearpi/user/update"; // 你的发布主题
        char pub_payload[256]; // 假设你的缓冲区大小为256，根据实际需要调整
        sprintf(pub_payload, "%s", uart_buff_ptr);
        MQTTMessage message;
        message.qos = 2;
        message.retained = 0;
        message.payload = (void*)pub_payload;
        message.payloadlen = strlen(pub_payload);

        printf("Publishing message: %s\n", (char*)message.payload);
        rc = MQTTPublish(&client, pub_topic, &message);
        printf("MQTTPublish: %d\n", rc);
        if (rc != 0) {
            printf("Return code from MQTT publish is %d\n", rc);
            if (rc == -1) {
                printf("MQTT connection lost, reconnecting...\n");
                NetworkDisconnect(&network);
                MQTTDisconnect(&client);
                osDelay(200);
                goto begin;
            }
        }
    }
}

/// @brief //串口初始化
/// @param  
static void UART_Task(void)
{
    uint8_t uart_buff[UART_BUFF_SIZE] = {0};
    uart_buff_ptr = uart_buff;
    uint32_t ret;

    WifiIotUartAttribute uart_attr = {
        .baudRate = 9600, // 波特率9600
        .dataBits = 8,      // 数据位8
        .stopBits = 1,      // 停止位1
        .parity = 0,        // 无校验
    };

    // 初始化UART驱动
    ret = UartInit(WIFI_IOT_UART_IDX_1, &uart_attr, NULL);
    if (ret != WIFI_IOT_SUCCESS)
    {
        printf("Failed to init uart! Err code = %d\n", ret);
        return;
    }
    while (1)
    {
        // 通过串口1接收数据
        UartRead(WIFI_IOT_UART_IDX_1, uart_buff_ptr, UART_BUFF_SIZE);
        usleep(1000000);
        printf("%s\r\n",uart_buff_ptr);
    }
}

static void MQTT_Demo(void)
{
    osThreadAttr_t attr;

    attr.name = "MQTT_DemoTask";
    attr.attr_bits = 0U;
    attr.cb_mem = NULL;
    attr.cb_size = 0U;
    attr.stack_mem = NULL;
    attr.stack_size = 1024 * 8; //5120
    attr.priority = osPriorityNormal;

    if (osThreadNew((osThreadFunc_t)MQTT_DemoTask, NULL, &attr) == NULL) {
        printf("[MQTT_Demo] Failed to create MQTT_DemoTask!\n");
    }

    // attr.name = "UART_Task";
    // attr.stack_size = ;  // 确保足够大
    if (osThreadNew((osThreadFunc_t)UART_Task, NULL, &attr) == NULL)
    {
        printf("[UART_Task] Failed to create UART_Task!\n");
    }
    else
    {
        printf("[UART_Task] Create UART_Task success!\n");
    }

}

APP_FEATURE_INIT(MQTT_Demo);
