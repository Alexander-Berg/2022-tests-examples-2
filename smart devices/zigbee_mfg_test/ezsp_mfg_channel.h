#pragma once

#include "i_mfg_channel.h"

#include <smart_devices/libs/zigbee/ezsp/ezsp.h>

class EzspMfgChannel
    : public IMfgChannel,
      public zigbee::IEzspListener,
      public std::enable_shared_from_this<EzspMfgChannel> {
public:
    EzspMfgChannel(const std::string& port);

private:
    void start(std::shared_ptr<IListener> listener) override;
    void stop() override;

    Eui64 getEui64() override;

    void setChannel(uint8_t channel) override;

    void setPower(int8_t power) override;

    void sendPacket(const std::vector<uint8_t>& payload) override;

    void onCounterRollover(EmberCounterType type) override;

    void onStackStatus(EzspStatus status) override;

    void onMessageSent(
        EmberOutgoingMessageType type,
        uint16_t indexOrDestination,
        const EmberApsFrame& apsFrame,
        uint8_t messageTag,
        EmberStatus status,
        const std::vector<uint8_t>& message) override;

    void onIncomingMessage(
        EmberIncomingMessageType type,
        const EmberApsFrame& apsFrame,
        uint8_t lastHopLqi,
        int8_t lastHopRssi,
        EmberNodeId sender,
        uint8_t bindingIndex,
        uint8_t addressIndex,
        const std::vector<uint8_t>& message) override;

    void onMfglibRx(uint8_t lqi, int8_t rssi, const std::vector<uint8_t>& payload) override;

    void onError(EzspStatus status) override;

private:
    const std::string& port_;
    zigbee::Ezsp& ezsp_;

    std::shared_ptr<IListener> listener_;
};
