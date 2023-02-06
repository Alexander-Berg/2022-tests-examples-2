#pragma once

#include "i_mfg_channel.h"

#include <smart_devices/libs/telink/hci/hci.h>
#include <smart_devices/libs/telink/hci/mfg_commands.h>

#include <yandex_io/libs/threading/i_callback_queue.h>

#include <future>

class TelinkMfgChannel
    : public IMfgChannel,
      public telink::MfgCommandHandler<TelinkMfgChannel>,
      public std::enable_shared_from_this<TelinkMfgChannel> {
public:
    TelinkMfgChannel(const std::string& port);

    template <class Command>
    telink::HciStatus handle(Command cmd);

private:
    void start(std::shared_ptr<IListener> listener) override;
    void stop() override;

    Eui64 getEui64() override;

    void setChannel(uint8_t channel) override;

    void setPower(int8_t power) override;

    void sendPacket(const std::vector<uint8_t>& payload) override;

private:
    const std::unique_ptr<telink::Hci> hci_;
    const std::unique_ptr<quasar::ICallbackQueue> callbackQueue_;

    std::shared_ptr<IListener> listener_;

    std::promise<Eui64> eui64Promise_;
};
