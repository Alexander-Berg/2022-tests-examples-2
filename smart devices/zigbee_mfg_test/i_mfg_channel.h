#pragma once

#include <cstdint>
#include <vector>

class IMfgChannel {
public:
    using Eui64 = std::array<uint8_t, 8>;

    class IListener {
    public:
        virtual ~IListener();

        virtual void onPacketReceived(uint8_t lqi, int8_t rssi, const std::vector<uint8_t>& payload) = 0;
    };

    virtual ~IMfgChannel();

    virtual void start(std::shared_ptr<IListener> listener) = 0;
    virtual void stop() = 0;

    virtual Eui64 getEui64() = 0;

    virtual void setChannel(uint8_t channel) = 0;

    virtual void setPower(int8_t power) = 0;

    virtual void sendPacket(const std::vector<uint8_t>& payload) = 0;
};
