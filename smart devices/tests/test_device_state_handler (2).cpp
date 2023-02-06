#include <smart_devices/platforms/yandexstation/leds/device_state_handler.h>

#include <library/cpp/testing/unittest/registar.h>

#include <yandex_io/libs/configuration/configuration.h>
#include <yandex_io/libs/device/device.h>
#include <yandex_io/modules/leds/led_controller/null_led_controller.h>
#include <yandex_io/modules/leds/led_manager/led_manager.h>
#include <yandex_io/modules/leds/led_manager/ng/default_led_devices.h>
#include <yandex_io/tests/testlib/unittest_helper/unit_test_fixture.h>

#include <memory>
#include <numeric>
#include <string>

using namespace quasar;

class TestLedManager: public LedManager {
public:
    TestLedManager()
        : LedManager(std::make_unique<DefaultLedDevices>(std::make_unique<NullLedController>()), ".")
    {
        listeningPattern_ = std::make_shared<ListeningPattern>(getPattern("activate-alisa.led"), 45.0);
    }

    void play(std::shared_ptr<AnimationConductor> conductor) override {
        lastAnimation_ = conductor->getCurrentComposition()->getAnimations().front()->getName();
    }

    std::shared_ptr<LedPattern> getPattern(const std::string& name) const override {
        return std::make_shared<LedPattern>(1, name, ledDevices_->getDefaultDevice());
    }

    std::shared_ptr<ListeningPattern> getListeningPattern(double doaAngle) const override {
        listeningPattern_ = std::make_shared<ListeningPattern>(getPattern("activate-alisa.led"), doaAngle);
        return listeningPattern_;
    }

    mutable std::shared_ptr<ListeningPattern> listeningPattern_;
    std::string lastAnimation_;
};

Y_UNIT_TEST_SUITE_F(YandexStationSDKStateHandler, QuasarUnitTestFixture) {
    Y_UNIT_TEST(TestIdleByDefault) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler stateHandler(testLedManager);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");
    }

    Y_UNIT_TEST(TestConfiguringState) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler stateHandler(testLedManager);
        YandexIO::SDKState deviceState;

        deviceState.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "configure.led");
    }

    Y_UNIT_TEST(TestUpdateAnimations) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler stateHandler(testLedManager);
        YandexIO::SDKState deviceState;

        /* Simple test Update when idle */
        deviceState.updateState.isCritical = true;
        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "progress.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::APPLYING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "progress.led");

        /* Not critical OTA should be silent */
        deviceState.updateState.isCritical = false;
        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::APPLYING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");

        /* When alarm/timer is playing -> it's more important than update */
        deviceState.updateState.isCritical = true;
        deviceState.isTimerPlaying = true;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.isTimerPlaying = false;

        /* Check that update is more important than any animation */
        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "progress.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::APPLYING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "progress.led");

    }

    Y_UNIT_TEST(TestBluetoothIsPlayingAnimation) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler stateHandler(testLedManager);
        YandexIO::SDKState deviceState;
        auto bluetoothStateListener = stateHandler.getBluetoothStateListener().lock();
        bluetoothStateListener->onBtPlaying(true);

        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "bluetooth_playing.led");

        /* Even with Bluetooth Stream In Alice animations should be played because Alice is still active with BT on JBL */
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "bluetooth_playing.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "bluetooth_playing.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "bluetooth_playing.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;
    }

    Y_UNIT_TEST(TestTimerAnimations) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler stateHandler(testLedManager);
        YandexIO::SDKState deviceState;

        deviceState.isTimerPlaying = true;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
        stateHandler.onSDKState(deviceState);
        /* When timer is playing -> it's more important than update */
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::APPLYING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        stateHandler.getBluetoothStateListener().lock()->onBtPlaying(true);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");
    }

    Y_UNIT_TEST(TestAliceAnimations) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler stateHandler(testLedManager);
        YandexIO::SDKState deviceState;

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "activate-alisa.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "thinking.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "speaking.led");

        /* Currently alice can't work when BT is played, so show bt animation */
        auto bluetoothStateListener = stateHandler.getBluetoothStateListener().lock();
        bluetoothStateListener->onBtPlaying(true);
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "bluetooth_playing.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "bluetooth_playing.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "bluetooth_playing.led");

        bluetoothStateListener->onBtPlaying(false);
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "activate-alisa.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "thinking.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "speaking.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");
    }

    Y_UNIT_TEST(TestDoaApply) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler stateHandler(testLedManager);
        auto doaListener = stateHandler.getDoaListener();

        YandexIO::SDKState deviceState;
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "activate-alisa.led");

        auto doublesEquals = [](double left, double right) -> bool {
            return std::abs(left - right) < std::numeric_limits<double>::epsilon();
        };

        YandexIO::ChannelData chData;
        chData.isForRecognition = true;
        auto testDoaApply = [&](double doa) {
            chData.meta.doaAngle = doa;
            doaListener->onAudioData({chData});
            UNIT_ASSERT_C(doublesEquals(testLedManager->listeningPattern_->getDoaAngle(), doa),
                          "Expected " << doa << ", but got " << testLedManager->listeningPattern_->getDoaAngle());
        };
        /* Check that Device State Handler set up DOA angle to listening pattern */
        testDoaApply(45.0);
        testDoaApply(111.1);
        testDoaApply(345.0);
        testDoaApply(0.0);

        /* Change animation and than get back to LISTENING to check that doa will be applied */
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "activate-alisa.led");
        /* Check that Device State Handler stil set up DOA angle to listening pattern */
        testDoaApply(45.0);
        testDoaApply(111.1);
        testDoaApply(345.0);
        testDoaApply(0.0);
    }

    Y_UNIT_TEST(TestNotificationAnimations) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler stateHandler(testLedManager);
        YandexIO::SDKState deviceState;

        /* No notification */
        deviceState.notificationState = YandexIO::SDKState::NotificationState::NONE;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");

        /* Has notification */
        deviceState.notificationState = YandexIO::SDKState::NotificationState::AVAILABLE;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "notification_available.led");

        /* Alice animation is more important */
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "speaking.led");
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::NONE;

        /* Update animation is more important */
        deviceState.updateState.isCritical = true;
        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "progress.led");
        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::NONE;
        deviceState.updateState.isCritical = false;

        /* Alarm/timer animation is more important */
        deviceState.isTimerPlaying = true;
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");
        deviceState.isTimerPlaying = false;

        /* For MVP BT is more important */
        auto bluetoothStateListener = stateHandler.getBluetoothStateListener().lock();
        bluetoothStateListener->onBtPlaying(true);
        stateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "bluetooth_playing.led");
    }
}
