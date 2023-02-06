#include <smart_devices/platforms/jbl_link/common/device_state_handler.h>

#include <library/cpp/testing/unittest/registar.h>

#include <yandex_io/libs/configuration/configuration.h>
#include <yandex_io/libs/device/device.h>
#include <yandex_io/modules/leds/led_controller/null_led_controller.h>
#include <yandex_io/modules/leds/led_manager/led_manager.h>
#include <yandex_io/modules/leds/led_manager/ng/default_led_devices.h>
#include <yandex_io/tests/testlib/unittest_helper/unit_test_fixture.h>

#include <memory>
#include <string>

using namespace quasar;

class TestLedManager: public LedManager {
public:
    TestLedManager()
        : LedManager(std::make_unique<DefaultLedDevices>(std::make_unique<NullLedController>()), ".")
    {
    }
    void play(std::shared_ptr<AnimationConductor> conductor) override {
        lastAnimation_ = conductor->getCurrentComposition()->getAnimations().front()->getName();
    }

    std::shared_ptr<LedPattern> getPattern(const std::string& name) const override {
        return std::make_shared<LedPattern>(1, name, ledDevices_->getDefaultDevice());
    }

    std::string lastAnimation_;
};

Y_UNIT_TEST_SUITE_F(JBLDeviceStateHandler, QuasarUnitTestFixture) {
    Y_UNIT_TEST(TestIdleByDefault) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler jblStateHandler(testLedManager);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");
    }

    Y_UNIT_TEST(TestConfiguringState) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler jblStateHandler(testLedManager);
        YandexIO::SDKState deviceState;

        deviceState.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "configure.led");

        /* When mics are muted user won't be able to use R2D2 to set up device, so show mute animation */
        auto micsStateListener = jblStateHandler.getMicsStateListener().lock();
        micsStateListener->onMuted();
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");
    }

    Y_UNIT_TEST(TestMutePriority) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler jblStateHandler(testLedManager);
        YandexIO::SDKState deviceState;
        auto micsStateListener = jblStateHandler.getMicsStateListener().lock();
        auto dataResetStateListener = jblStateHandler.getDataResetStateListener().lock();
        auto bluetoothStateListener = jblStateHandler.getBluetoothStateListener().lock();
        micsStateListener->onMuted();
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");

        /* Timer animation is showed even in update */
        deviceState.isTimerPlaying = true;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.isTimerPlaying = false;
        jblStateHandler.onSDKState(deviceState);
        /* Even with muted mics show Data Reset animation */
        dataResetStateListener->onDataResetWaitConfirm();
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "confirm_data_reset.led");

        dataResetStateListener->onDataResetExecuting();
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "data_reset_progress.led");
        dataResetStateListener->onDataResetCanceled();

        /* Mics are still muted. User won't be able to use R2D2 to set up. Show that mics are muted */
        deviceState.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");

        /* When mics are muted and Alice works -> show mute*/
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;

        /* With mics muted -> show MUTE animation even when bt is playing */

        bluetoothStateListener->onBtPlaying(true);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");

        bluetoothStateListener->onBtPlaying(false);
        micsStateListener->onUnmuted();
        /* Now device is simply idle after unmute */
        deviceState.configurationState = YandexIO::SDKState::ConfigurationState::CONFIGURED;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");
    }

    Y_UNIT_TEST(TestUpdateAnimations) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler jblStateHandler(testLedManager);
        YandexIO::SDKState deviceState;

        /* Simple test Update when idle */
        deviceState.updateState.isCritical = true;
        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "progress.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::APPLYING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "apply_ota.led");

        /* Not critical OTA should be silent */
        deviceState.updateState.isCritical = false;
        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::APPLYING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");

        /* When alarm/timer is playing -> it's more important than update */
        deviceState.updateState.isCritical = true;
        deviceState.isTimerPlaying = true;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.isTimerPlaying = false;

        /* Check that update is more important than MUTE animation */
        auto micsStateListener = jblStateHandler.getMicsStateListener().lock();
        micsStateListener->onMuted();
        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "progress.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::APPLYING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "apply_ota.led");

    }

    Y_UNIT_TEST(TestBluetoothIsPlayingAnimation) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler jblStateHandler(testLedManager);
        YandexIO::SDKState deviceState;
        auto bluetoothStateListener = jblStateHandler.getBluetoothStateListener().lock();

        bluetoothStateListener->onBtPlaying(true);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "bluetooth_playing.led");

        /* Even with Bluetooth Stream In Alice animations should be played because Alice is still active with BT on JBL */
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "activate-alisa.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "thinking.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "speaking.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;
        /* Mute has higher priority than bluetooth */
        auto micsStateListener = jblStateHandler.getMicsStateListener().lock();
        micsStateListener->onMuted();
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");
    }

    Y_UNIT_TEST(TestTimerAnimations) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler jblStateHandler(testLedManager);
        YandexIO::SDKState deviceState;

        auto dataResetStateListener = jblStateHandler.getDataResetStateListener().lock();

        deviceState.isTimerPlaying = true;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
        jblStateHandler.onSDKState(deviceState);
        /* When timer is playing -> it's more important than update */
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::APPLYING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        /* Even with muted mics show Data Reset animation */
        deviceState.updateState.state = YandexIO::SDKState::UpdateState::State::NONE;
        dataResetStateListener->onDataResetWaitConfirm();
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        dataResetStateListener->onDataResetExecuting();
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        /* even with muted mics show timer animation */
        auto micsStateListener = jblStateHandler.getMicsStateListener().lock();
        micsStateListener->onMuted();
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        micsStateListener->onUnmuted();
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");

        jblStateHandler.getBluetoothStateListener().lock()->onBtPlaying(true);
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "timer.led");
    }

    Y_UNIT_TEST(TestAliceAnimations) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler jblStateHandler(testLedManager);
        YandexIO::SDKState deviceState;

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "activate-alisa.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "thinking.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "speaking.led");

        /* Even with Bluetooth Stream In Alice animations should be played because Alice is still active with BT on JBL */
        auto btListener = jblStateHandler.getBluetoothStateListener().lock();
        btListener->onBtPlaying(true);
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "activate-alisa.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "thinking.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "speaking.led");
        btListener->onBtPlaying(false);

        /* When mics are muted and Alice works -> show mute*/
        auto micsStateListener = jblStateHandler.getMicsStateListener().lock();
        micsStateListener->onMuted();
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::LISTENING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::THINKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");

        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "mute_mics.led");

        micsStateListener->onUnmuted();
        deviceState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;
        jblStateHandler.onSDKState(deviceState);
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "idle.led");

    }

    Y_UNIT_TEST(TestDataResetAnimation) {
        auto testLedManager = std::make_shared<TestLedManager>();
        DeviceStateHandler jblStateHandler(testLedManager);
        auto dataResetStateListener = jblStateHandler.getDataResetStateListener().lock();
        YandexIO::SDKState deviceState;

        dataResetStateListener->onDataResetWaitConfirm();
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "confirm_data_reset.led");

        dataResetStateListener->onDataResetExecuting();
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "data_reset_progress.led");

        /* Even in mute show data reset */
        auto micsStateListener = jblStateHandler.getMicsStateListener().lock();
        micsStateListener->onMuted();
        dataResetStateListener->onDataResetWaitConfirm();
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "confirm_data_reset.led");

        dataResetStateListener->onDataResetExecuting();
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "data_reset_progress.led");

        /* Even in bluetooth show data reset */
        micsStateListener->onUnmuted();
        jblStateHandler.getBluetoothStateListener().lock()->onBtPlaying(true);
        jblStateHandler.onSDKState(deviceState);
        dataResetStateListener->onDataResetWaitConfirm();
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "confirm_data_reset.led");

        dataResetStateListener->onDataResetExecuting();
        UNIT_ASSERT_VALUES_EQUAL(testLedManager->lastAnimation_, "data_reset_progress.led");
    }
}
