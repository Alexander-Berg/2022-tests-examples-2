#include <smart_devices/platforms/jbl_link/portable/idle_state_handler/idle_state_handler_portable.h>

#include <yandex_io/capabilities/file_player/interfaces/mocks/mock_i_file_player_capability.h>
#include <yandex_io/libs/base/utils.h>
#include <yandex_io/libs/logging/logging.h>
#include <yandex_io/tests/testlib/null_sdk/null_sdk_interface.h>
#include <yandex_io/tests/testlib/test_utils.h>
#include <yandex_io/tests/testlib/unittest_helper/unit_test_fixture.h>

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/gmock_in_unittest/gmock.h>
#include <util/generic/scope.h>

#include <future>
#include <string>

using namespace jbl_link_portable;
using namespace YandexIO;
using namespace quasar;
using namespace testing;

namespace {

    class MockSDK: public YandexIO::NullSDKInterface {
    public:
        MockSDK() = default;
        MOCK_METHOD(void, setAllowUpdate, (bool, bool), (override));
    };

} // namespace

Y_UNIT_TEST_SUITE_F(TestJblLinkPortable, QuasarUnitTestFixtureWithoutIpc) {
    Y_UNIT_TEST(testIdleStateHandler)
    {
        const auto device = getDeviceForTests();
        const auto sdk = std::make_shared<MockSDK>();
        const auto filePlayerCapability = std::make_shared<YandexIO::MockIFilePlayerCapability>();
        const auto updateAllowController = std::make_shared<UpdateAllowController>(sdk, device->telemetry());
        const auto powerOffController = std::make_shared<JBLPowerOffController>(filePlayerCapability, "touch turn_off", "touch reboot");
        const auto idleStateHandlerPortable = std::make_shared<IdleStateHandlerPortable>(powerOffController, updateAllowController, std::chrono::seconds(1), std::chrono::seconds(3));

        Y_DEFER {
            std::remove("turn_off");
        };

        std::promise<void> expectation;

        auto waitExpectation = [&]() {
            expectation.get_future().get();
            expectation = std::promise<void>();
        };

        {
            EXPECT_CALL(*sdk, setAllowUpdate(false, false)).WillOnce(Invoke([&]() {
                                                               expectation.set_value();
                                                           }))
                .RetiresOnSaturation();
            YIO_LOG_INFO("Start update allow controller");
            // At start we prohibit update. Wait default values
            updateAllowController->start();
            waitExpectation();
        }

        {
            // init Charging state. Power state (battery state) is not inited -> updates are not allowed
            EXPECT_CALL(*sdk, setAllowUpdate(false, false)).WillOnce(Invoke([&]() {
                                                               expectation.set_value();
                                                           }))
                .RetiresOnSaturation();
            YIO_LOG_INFO("Allow by charging state");
            updateAllowController->setAllowByChargingState(true);
            waitExpectation();
        }

        {
            // init sdk idle state. power state is steal unknown. updates are not allowed
            EXPECT_CALL(*sdk, setAllowUpdate(false, false)).WillOnce(Invoke([&]() {
                                                               expectation.set_value();
                                                           }))
                .RetiresOnSaturation();
            YIO_LOG_INFO("Send idle device state again");
            YandexIO::SDKState sdkState;
            sdkState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;
            idleStateHandlerPortable->onSDKState(sdkState);
            waitExpectation();
        }

        {
            // device is idle. Allowed by Charging state and Power State
            EXPECT_CALL(*sdk, setAllowUpdate(true, true)).WillOnce(Invoke([&]() {
                                                             expectation.set_value();
                                                         }))
                .RetiresOnSaturation();
            YIO_LOG_INFO("Set allow by power");
            updateAllowController->setAllowByPower(true);
            waitExpectation();
        }

        // power and battery state are inited from this point

        {
            // SDK is not idle. Only Crit updates are allowed
            EXPECT_CALL(*sdk, setAllowUpdate(false, true)).WillOnce(Invoke([&]() {
                                                              expectation.set_value();
                                                          }))
                .RetiresOnSaturation();
            YIO_LOG_INFO("Send idle device state again");
            YandexIO::SDKState sdkState;
            sdkState.aliceState.state = YandexIO::SDKState::AliceState::State::SPEAKING;
            idleStateHandlerPortable->onSDKState(sdkState);
            waitExpectation();
        }

        {
            // device is idle. Allowed by Charging state and Power State
            EXPECT_CALL(*sdk, setAllowUpdate(true, true)).WillOnce(Invoke([&]() {
                                                             expectation.set_value();
                                                         }))
                .RetiresOnSaturation();
            YIO_LOG_INFO("Send idle device state again");
            YandexIO::SDKState sdkState;
            sdkState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;
            idleStateHandlerPortable->onSDKState(sdkState);
            waitExpectation();
        }

        {
            // Send Updating state
            YIO_LOG_INFO("Send Updating state");
            YandexIO::SDKState sdkState;
            sdkState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;
            sdkState.updateState.state = YandexIO::SDKState::UpdateState::State::DOWNLOADING;
            idleStateHandlerPortable->onSDKState(sdkState);
            // Turn Off timer is 3 sec. Make sure that device will not turn off during
            const auto res = TestUtils::doUntil([]() { return fileExists("turn_off"); }, 5000);
            UNIT_ASSERT(!res);
        }

        {
            // device is idle. Allowed by Charging state and Power State
            // Device is idle and should turn off in 3 sec by PowerOffTimeout from
            // idleStateHandlerPortable
            YIO_LOG_INFO("Send idle device state again");
            YandexIO::SDKState sdkState;
            sdkState.aliceState.state = YandexIO::SDKState::AliceState::State::IDLE;
            idleStateHandlerPortable->onSDKState(sdkState);
            // Don't send anything, wait for power off
            TestUtils::waitUntil([]() { return fileExists("turn_off"); });
        }
    }
}
