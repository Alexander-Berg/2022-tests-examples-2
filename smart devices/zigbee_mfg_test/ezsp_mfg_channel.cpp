#include "ezsp_mfg_channel.h"

#include <yandex_io/libs/logging/logging.h>

#include <util/string/hex.h>

namespace {

    bool isOk(EzspStatus status) {
        constexpr std::array<EzspStatus, 15> goodSignals = {
            EZSP_SUCCESS, EZSP_ASH_IN_PROGRESS, EZSP_NO_RX_DATA,
            EZSP_ASH_STARTED, EZSP_ASH_CONNECTED, EZSP_ASH_ACK_RECEIVED,
            EZSP_ASH_ACK_SENT, EZSP_ASH_NAK_RECEIVED, EZSP_ASH_NAK_SENT,
            EZSP_ASH_RST_RECEIVED, EZSP_ASH_RST_SENT, EZSP_ASH_STATUS,
            EZSP_ASH_TX, EZSP_ASH_RX, EZSP_NO_ERROR};
        return std::find(goodSignals.begin(), goodSignals.end(), status) == goodSignals.end();
    }

} // namespace

EzspMfgChannel::EzspMfgChannel(const std::string& port)
    : port_(port)
    , ezsp_(zigbee::Ezsp::getInstance())
{
}

void EzspMfgChannel::start(std::shared_ptr<IListener> listener) {
    listener_ = std::move(listener);

    ezsp_.setListener(weak_from_this());
    ezsp_.start(port_);

    ezsp_.mfglibStart();
}

void EzspMfgChannel::stop() {
    ezsp_.mfglibEnd();

    ezsp_.stop();

    listener_.reset();
}

EzspMfgChannel::Eui64 EzspMfgChannel::getEui64() {
    Eui64 eui64;
    ezsp_.getEui64(eui64.data());
    return eui64;
}

void EzspMfgChannel::setChannel(uint8_t channel) {
    ezsp_.mfglibSetChannel(channel);
    YIO_LOG_DEBUG("mfglib channel: " << (uint32_t)ezsp_.mfglibGetChannel());
}

void EzspMfgChannel::setPower(int8_t power) {
    ezsp_.mfglibSetPower(power);
    YIO_LOG_DEBUG("mfglib power: " << (int32_t)ezsp_.mfglibGetPower());
}

void EzspMfgChannel::sendPacket(const std::vector<uint8_t>& payload) {
    ezsp_.mfglibSendPacket(payload);
}

void EzspMfgChannel::onCounterRollover(EmberCounterType /* type */) {
}

void EzspMfgChannel::onStackStatus(EzspStatus /* status */) {
}

void EzspMfgChannel::onMessageSent(
    EmberOutgoingMessageType /* type */,
    uint16_t /* indexOrDestination */,
    const EmberApsFrame& /* apsFrame */,
    uint8_t /* messageTag */,
    EmberStatus /* status */,
    const std::vector<uint8_t>& /* message */) {
}

void EzspMfgChannel::onIncomingMessage(
    EmberIncomingMessageType /* type */,
    const EmberApsFrame& /* apsFrame */,
    uint8_t /* lastHopLqi */,
    int8_t /* lastHopRssi */,
    EmberNodeId /* sender */,
    uint8_t /* bindingIndex */,
    uint8_t /* addressIndex */,
    const std::vector<uint8_t>& /* message */) {
}

void EzspMfgChannel::onMfglibRx(uint8_t lqi, int8_t rssi, const std::vector<uint8_t>& payload) {
    YIO_LOG_DEBUG("mfglib packet:"
                  << " lqi " << (int)lqi
                  << " rssi " << (int)rssi
                  << " payload " << HexEncode(payload.data(), payload.size()));

    listener_->onPacketReceived(lqi, rssi, payload);
}

void EzspMfgChannel::onError(EzspStatus status) {
    // FUUUUU
    if (!isOk(status)) {
        exit(42);
    }
}
