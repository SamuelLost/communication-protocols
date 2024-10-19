#include "socket_can.h"
#include <linux/can.h>
#include <linux/can/raw.h>
#include <iostream>
#include <string>

float float_to_bytes(uint8_t *bytes) {
    float f;
    std::memcpy(&f, bytes, sizeof(f));
    return f;

}

int main() {
    SocketCan socket_can("can0");
    if (!socket_can.Init()) {
        std::cerr << "Failed to initialize CAN socket" << std::endl;
        return -1;
    }

    can_frame frame;

    while (1) {
        if(socket_can.ReadCanMessage(frame)) {
            switch(frame.can_id) {
                case 0x012:
                    std::cout << "Luminosidade: " << float_to_bytes(frame.data) << std::endl;
                    break;
                case 0x079: {
                    int16_t x = (frame.data[1] << 8) | frame.data[0];
                    int16_t y = (frame.data[3] << 8) | frame.data[2];
                    int16_t z = (frame.data[5] << 8) | frame.data[4];
                    std::cout << "Acelerometro: x=" << x << " y=" << y << " z=" << z << std::endl;
                    break;
                }
                case 0x080: {
                    int16_t temp = (frame.data[0] << 8) | frame.data[1];
                    int16_t hum = (frame.data[2] << 8) | frame.data[3];
                    std::cout << "Temperatura: " << temp << "ºC" << " Humidade: " << hum << "%" << std::endl;
                    break;
                }
                default:
                    std::cout << "Unknown CAN ID: " << std::hex << frame.can_id << std::endl;
                    break;
            }
        } 
    }
}