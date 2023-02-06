#include <smart_devices/platforms/yandexstation/leds/device_state_handler.h>

#include <library/cpp/testing/common/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex_io/modules/leds/led_controller/led_device.h>
#include <yandex_io/modules/leds/led_manager/led_manager.h>
#include <yandex_io/modules/leds/led_manager/ng/led_devices.h>
#include <yandex_io/modules/leds/led_manager/ng/animation_conductor.h>

#include <yandex_io/tests/testlib/unittest_helper/unit_test_fixture.h>

#include <chrono>
#include <memory>
#include <thread>

class DummyLedController: public quasar::LedController {
public:
    int getLedCount() const override {
        return 0;
    }

    void drawFrame(const quasar::LedCircle& colors) override {
        Y_UNUSED(colors);
    }

    quasar::rgbw_color readColor(const std::string& stringColor) override {
        Y_UNUSED(stringColor);
        return {};
    }
};

class DummyLedDevices: public LedDevices {
public:
    DummyLedDevices()
        : defaultDevice_{std::make_shared<DummyLedController>()}
        , devicesList_{defaultDevice_}
    {
    }

    const std::vector<std::shared_ptr<quasar::LedDevice>>& getDevicesList() const override {
        return devicesList_;
    }

    std::shared_ptr<quasar::LedController> getDefaultDevice() const override {
        return defaultDevice_;
    };

private:
    std::shared_ptr<quasar::LedController> defaultDevice_;
    std::vector<std::shared_ptr<quasar::LedDevice>> devicesList_;
};

class DummyLedManager: public quasar::LedManager {
public:
    DummyLedManager()
        : quasar::LedManager{std::make_shared<DummyLedDevices>(), ArcadiaSourceRoot() + "/smart_devices/platforms/yandexstation/data/ledpatterns"}
    {
    }
};

Y_UNIT_TEST_SUITE(Test) {
    Y_UNIT_TEST_F(Test, QuasarUnitTestFixtureWithoutIpc) {
        auto manager = std::make_shared<DummyLedManager>();
        auto device_state_handler = DeviceStateHandler(manager);
        YandexIO::SDKState listening_state;
        listening_state.isAlarmPlaying = false;
        listening_state.isTimerPlaying = false;
        listening_state.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        device_state_handler.onSDKState(listening_state);
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        device_state_handler.onSDKState(listening_state);
        YandexIO::SDKState thinking_state;
        thinking_state.isAlarmPlaying = false;
        thinking_state.isTimerPlaying = false;
        thinking_state.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        device_state_handler.onSDKState(thinking_state);
    }
}