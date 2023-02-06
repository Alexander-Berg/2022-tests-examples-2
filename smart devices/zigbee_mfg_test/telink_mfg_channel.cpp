#include "telink_mfg_channel.h"

#include <yandex_io/libs/base/named_callback_queue.h>
#include <yandex_io/libs/base/utils.h>
#include <yandex_io/libs/logging/logging.h>

TelinkMfgChannel::TelinkMfgChannel(const std::string& port)
    : hci_(std::make_unique<telink::Hci>(port))
    , callbackQueue_(std::make_unique<quasar::NamedCallbackQueue>("TelinkMfgChannel"))
{
}

void TelinkMfgChannel::start(std::shared_ptr<IListener> listener) {
    listener_ = std::move(listener);

    hci_->start(shared_from_this());
    hci_->send(telink::MfgStartRequest{});
}

void TelinkMfgChannel::stop() {
    hci_->send(telink::MfgStopRequest{});
    hci_->stop();

    listener_.reset();
}

TelinkMfgChannel::Eui64 TelinkMfgChannel::getEui64() {
    eui64Promise_ = std::promise<Eui64>();
    auto future = eui64Promise_.get_future();

    hci_->send(telink::MfgEui64Request{});

    if (future.wait_for(std::chrono::milliseconds(100)) != std::future_status::ready) {
        throw std::runtime_error("Timeout");
    }

    return future.get();
}

void TelinkMfgChannel::setChannel(uint8_t channel) {
    hci_->send(telink::MfgSetChannelRequest{
        .channel = channel,
    });
}

void TelinkMfgChannel::setPower(int8_t power) {
    hci_->send(telink::MfgSetPowerRequest{
        .power = power,
    });
}

void TelinkMfgChannel::sendPacket(const std::vector<uint8_t>& payload) {
    hci_->send(telink::MfgSendPacketRequest{
        .data = payload,
    });
}

template <>
telink::HciStatus TelinkMfgChannel::handle(telink::MfgEui64Response cmd) {
    YIO_LOG_DEBUG("EUI64: " << HexEncode(cmd.eui64, sizeof(cmd.eui64)));

    try {
        eui64Promise_.set_value(std::to_array(cmd.eui64));
    } catch (const std::future_error& e) {
        YIO_LOG_DEBUG("Unexpected response");
    }

    return telink::HciStatus::Success;
}

template <>
telink::HciStatus TelinkMfgChannel::handle(telink::MfgReceivePacketIndication cmd) {
    callbackQueue_->add([this, cmd = std::move(cmd)]() {
        YIO_LOG_DEBUG(
            "Received packet:"
            << " lqi " << static_cast<uint32_t>(cmd.lqi)
            << " rssi " << static_cast<int32_t>(cmd.rssi)
            << " length " << static_cast<uint32_t>(cmd.length)
            << " data " << quasar::Hex(cmd.data));

        listener_->onPacketReceived(cmd.lqi, cmd.rssi, {cmd.data.begin(), cmd.data.end() - 2});
    });

    return telink::HciStatus::Success;
}
