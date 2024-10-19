#include <arpa/inet.h>
#include <iostream>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <net/if.h>
#include <netinet/in.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <string>
#include <cstring>
#include <stdlib.h>
#include <unistd.h>

#define TAG_SOCKET_CAN "SOCKET_CAN"

struct SocketCan {
public:
    SocketCan(std::string const& interface_name = "can0");
    bool SendCanMessage(can_frame const& frame);
    bool ReadCanMessage(can_frame &frame);
    bool Init();
private:
    bool OpenCanSocket();
    bool BindCanSocket();
    bool CloseCanSocket();
private:
    sockaddr_can addr_can_;
    ifreq interface_request_;
    std::string interface_name_;
    int can_socket_;
};
