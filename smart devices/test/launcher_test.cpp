#include <yandex_io/android_sdk/libs/cpp/interfaces/audio_sink.h>
#include <yandex_io/android_sdk/libs/cpp/interfaces/launcher.h>
#include <yandex_io/android_sdk/libs/cpp/jni/capabilities/alice/jni_alice_capability.h>
#include <yandex_io/capabilities/alice/interfaces/i_alice_capability.h>
#include <yandex_io/scaffolding/proto/config.pb.h>
#include <smart_devices/platforms/android/all/cpp/launcher.h>

#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

namespace {
    std::shared_ptr<LauncherConfig> makeConfig() {
        auto result = std::make_shared<LauncherConfig>();
        if (auto* paths = result->mutable_paths()) {
            const auto arcadia = ArcadiaSourceRoot();
            const auto workingDir = GetWorkPath();
            paths->set_config_path(ArcadiaFromCurrentLocation(__SOURCE_FILE__, "../../src/main/assets/quasar.cfg"));
            paths->set_workdir_path(workingDir);

            auto& placeholders = *paths->mutable_config_placeholders();
            placeholders["QUASAR"] = arcadia + "/yandex_io/android_sdk/data";
            placeholders["DATA"] = workingDir;
            placeholders["FILES"] = workingDir;
            placeholders["APP_ID"] = "unknown_app";
            placeholders["APP_VERSION"] = "unknown_app_version";
            placeholders["SOFTWARE_VERSION"] = "unknown_software_version";
            placeholders["OS"] = "unknown_os";
            placeholders["OS_VERSION"] = "unknown_os_version";
            placeholders["DEVICE_TYPE"] = "unknown_device_type";
            placeholders["DEVICE_MANUFACTURER"] = "unknown_device_manufacturer";
            placeholders["CRYPTOGRAPHY_TYPE"] = "plainFile";
            placeholders["LOG_LEVEL"] = "debug";
            placeholders["USER_AGENT"] = "${APP_ID}/${APP_VERSION} (${DEVICE_MANUFACTURER} ${DEVICE_TYPE}; Android ${OS_VERSION})";
        }
        result->set_device_id("test-device-id");
        return result;
    }

    class MockAudioSink: public YandexIO::IAudioSink {
    public:
        void start(int channels, int sampleRate, int sampleSize) override {
            Y_UNUSED(channels, sampleRate, sampleSize);
        }
        void pause() override {
        }
        void resume() override {
        }
        void cancel() override {
        }
        void finish() override {
        }
        void pushData(std::span<const std::uint8_t> data) override {
            Y_UNUSED(data);
        }
    };
}

class TFullLauncherTest: public TTestBase {
public:
    void StartNotInitialized() {
        const auto underTest = YandexIO::createLauncher();
        UNIT_CHECK_GENERATED_EXCEPTION(underTest->start(), yexception);
    }

    void StartNoSink() {
        const auto underTest = YandexIO::createLauncher();
        underTest->initialize(makeConfig());
        UNIT_CHECK_GENERATED_EXCEPTION(underTest->start(), yexception);
    }

    void Startup() {
        const auto underTest = YandexIO::createLauncher();
        UNIT_ASSERT_EQUAL(nullptr, YandexIO::getNativeAliceCapabilityInterfaceForTest());
        underTest->initialize(makeConfig());
        UNIT_ASSERT_EQUAL(nullptr, YandexIO::getNativeAliceCapabilityInterfaceForTest());
        underTest->setAudioSink(std::make_shared<MockAudioSink>());
        underTest->start();

        auto* alice = YandexIO::getNativeAliceCapabilityInterfaceForTest();
        alice->toggleConversation(YandexIO::VinsRequest::createHardwareButtonClickEventSource());
    }

private:
    UNIT_TEST_SUITE(TFullLauncherTest);
    UNIT_TEST(StartNotInitialized);
    UNIT_TEST(StartNoSink);
    UNIT_TEST(Startup);
    UNIT_TEST_SUITE_END();
};

UNIT_TEST_SUITE_REGISTRATION(TFullLauncherTest);
