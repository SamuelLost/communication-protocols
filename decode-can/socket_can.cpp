#include "socket_can.h"

SocketCan::SocketCan(std::string const& interface_name) : interface_name_(interface_name) {
    memset(&addr_can_, 0, sizeof(addr_can_));
    memset(&interface_request_, 0, sizeof(interface_request_));
}

bool SocketCan::ReadCanMessage(can_frame &frame) {
    int nbytes = read(can_socket_, &frame, sizeof(struct can_frame));
    if (nbytes < 0) {
        // std::cerr << "Failed to read CAN message" << std::endl;
        return false;
    }
    return true;
}

bool SocketCan::SendCanMessage(can_frame const& frame) {
    int nbytes = write(can_socket_, &frame, sizeof(struct can_frame));
    if (nbytes < 0) {
        // std::cerr << "Failed to send CAN message" << std::endl;
        return false;
    }
    return true;
}

bool SocketCan::OpenCanSocket() {
    can_socket_ = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (can_socket_ < 0) {
        return false;
    }
    return true;
}

bool SocketCan::Init() {
    if (!OpenCanSocket()) {
        return false;
    }
    if (!BindCanSocket()) {
        return false;
    }
    return true;
}

bool SocketCan::BindCanSocket() {
    strcpy(interface_request_.ifr_name, interface_name_.c_str());
    
    addr_can_.can_family = AF_CAN;
    addr_can_.can_ifindex = interface_request_.ifr_ifindex;

    if (ioctl(can_socket_, SIOCGIFINDEX, &interface_request_) < 0) {
        // std::cerr << "Failed to get CAN interface index" << std::endl;
        return false;
    }
    if (bind(can_socket_, (struct sockaddr*)&addr_can_, sizeof(addr_can_)) < 0) {
        // std::cerr << "Failed to bind CAN socket" << std::endl;
        return false;
    }
    return true;
}

bool SocketCan::CloseCanSocket() {
    if (close(can_socket_) < 0) {
        // std::cerr << "Failed to close CAN socket" << std::endl;
        return false;
    }
    return true;
}


// Path: device/snappautomotive/rpi4_car/can/can-vhal-tcc/SocketCan.h
