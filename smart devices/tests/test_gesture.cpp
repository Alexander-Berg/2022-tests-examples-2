#include <smart_devices/platforms/yandexmini/sensor/gestures/gesture_data_listener.h>

#include <smart_devices/platforms/yandexmini/sensor/sensor_reader.h>

#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <yandex_io/tests/testlib/unittest_helper/unit_test_fixture.h>

#include <fstream>
#include <iterator>
#include <sstream>
#include <vector>

using namespace quasar;

Y_UNIT_TEST_SUITE_F(TestGestures, QuasarUnitTestFixture) {
    Y_UNIT_TEST(testHistoryBuffer) {
        const double EPS = 1E-6;
        HistoryBuffer buffer(5, 5);
        buffer.push(1);
        buffer.push(2);
        buffer.push(6);
        UNIT_ASSERT_VALUES_EQUAL(buffer.getMedian(), 5);
        buffer.push(1);
        UNIT_ASSERT_DOUBLES_EQUAL(buffer.getMean(), 3, EPS);
        UNIT_ASSERT_VALUES_EQUAL(buffer.getMedian(), 2);
        UNIT_ASSERT_DOUBLES_EQUAL(buffer.getStd(), 2.09761769634, EPS);
        buffer.push(0);
        buffer.push(0);
        buffer.push(0);
        buffer.push(0);
        buffer.push(0);
        UNIT_ASSERT_DOUBLES_EQUAL(buffer.getMean(), 0, EPS);
        UNIT_ASSERT_DOUBLES_EQUAL(buffer.getStd(), 0, EPS);
    }

    Y_UNIT_TEST(testGestureEventNames)
    {
        for (int i = 0; i < Gesture::EVENT_TYPES_COUNT; i++) {
            Gesture::Event e = static_cast<Gesture::Event>(i);
            Gesture g(e);
            UNIT_ASSERT(!g.str().empty());
        }
    }

    void testData(std::string filename, SensorReader<uint16_t>::Listener & listener) {
        std::ifstream fin(ArcadiaSourceRoot() + "/smart_devices/platforms/yandexmini/sensor/gestures/tests/gestures_test_data/" + filename, std::ios::binary);
        YIO_LOG_INFO("Fail: " << fin.fail());
        fin.seekg(0, fin.end);
        int length = fin.tellg();
        fin.seekg(0, fin.beg);
        YIO_LOG_INFO("length " << length);

        std::vector<SensorReader<uint16_t>::Data> buffer(length / sizeof(SensorReader<uint16_t>::Data));
        fin.read((char*)buffer.data(), length);

        for (const auto& data : buffer) {
            listener.onDataReady(data, "");
        }
    }

    void testDataCsv(std::string filename, SensorReader<uint16_t>::Listener & listener) {
        std::ifstream fin(ArcadiaSourceRoot() + "/smart_devices/platforms/yandexmini/sensor/gestures/tests/gestures_test_data/" + filename);

        UNIT_ASSERT(fin);

        for (std::string s; std::getline(fin, s);) {
            long long int ts = 0;
            int error = 0;
            int value = 0;
            YIO_LOG_DEBUG(s);
            UNIT_ASSERT(sscanf(s.c_str(), "%lld,%d,%d", &ts, &error, &value) == 3);
            SensorReader<uint16_t>::Data data{(uint16_t)value, error};

            listener.onDataReady(data, "");
        }
    }

    int gestureValueToPenalty(double value) {
        return std::min(int(std::abs(value) + 0.5), 10);
    }

    int countFalsePositives(const GestureDataListener::Settings& settings) {
        GestureDataListener gestureDataListener(settings);

        int penalty = 0;

        gestureDataListener.onDoubleSwingGesture = [&penalty]() {
            penalty += 1;
        };
        gestureDataListener.onLowHoldGesture = [&penalty]() {
            penalty += 1;
        };
        gestureDataListener.onRangeGestureStart = [&penalty]() {
            penalty += 1;
        };
        gestureDataListener.onRangeGestureEnd = [&penalty]() {
            penalty += 0;
        };
        gestureDataListener.onRangeGestureValue = [&penalty](double value) {
            penalty += gestureValueToPenalty(value);
        };

        const std::string files[]{
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_01.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_hand_over_01.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_lean_over_01.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_lean_over_02.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_33cm_shelf_01.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_33cm_shelf_02.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_42cm_shelf_01.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_42cm_shelf_02.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_51cm_shelf_01.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_51cm_shelf_02.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_60cm_shelf_01.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_68cm_shelf_01.csv",
            "no_actions/mp_calibrated_FF98F029E72264BA4792A68E_121cm_lamp_01.csv"};

        for (auto f : files) {
            gestureDataListener.clearState();
            testDataCsv(f, gestureDataListener);
        }

        YIO_LOG_INFO("False positives penalty: " << penalty);

        return penalty;
    }

    Y_UNIT_TEST(testRangeGestureFalsePositives) {
        GestureDataListener::Settings settings;
        settings.tofIsCalibrated = true;
        settings.doubleSwingGesture.enabled = false;
        settings.lowHoldGesture.enabled = false;
        settings.rangeGesture.enabled = true;

        const int penalty = countFalsePositives(settings);

        // This value is based on the current algorithm and test data set.
        // Ideally it should be zero, but can be increased in favour of true positives
        UNIT_ASSERT(penalty == 13);
    }

    Y_UNIT_TEST(testLowHoldGestureFalsePositives) {
        GestureDataListener::Settings settings;
        settings.tofIsCalibrated = true;
        settings.doubleSwingGesture.enabled = false;
        settings.lowHoldGesture.enabled = true;
        settings.rangeGesture.enabled = false;

        const int penalty = countFalsePositives(settings);

        // This value is based on the current algorithm and test data set.
        // Ideally it should be zero, but can be increased in favour of true positives
        UNIT_ASSERT(penalty == 0);
    }

    Y_UNIT_TEST(testGestureDoubleSwing) {
        GestureDataListener::Settings settings;
        settings.tofIsCalibrated = true;
        settings.doubleSwingGesture.enabled = true;
        GestureDataListener gestureDataListener(settings);

        bool triggered = false;
        gestureDataListener.onDoubleSwingGesture = [&triggered]() {
            triggered = true;
        };
        testData("double_swing_gesture_same_height.raw", gestureDataListener);
        UNIT_ASSERT(triggered);
        triggered = false;
        testData("double_swing_gesture_different_height.raw", gestureDataListener);
        UNIT_ASSERT(!triggered);
    }

    Y_UNIT_TEST(testGestureShutUp) {
        GestureDataListener::Settings settings;
        settings.tofIsCalibrated = true;
        settings.lowHoldGesture.enabled = true;
        GestureDataListener gestureDataListener(settings);

        const std::string files[]{
            "enough/mp_calibrated_FF98F029E72264BA4792A68E_01.csv",
            "enough/mp_calibrated_FF98F029E72264BA4792A68E_02.csv",
            "enough/mp_calibrated_FF98F029E72264BA4792A68E_03.csv",
            "enough/mp_calibrated_FF98F029E72264BA4792A68E_04.csv",
            "enough/mp_calibrated_FF98F029E72264BA4792A68E_05.csv"};

        for (auto f : files) {
            bool triggered = false;
            int sideEffects = 0;
            gestureDataListener.onLowHoldGesture = [&triggered]() {
                triggered = true;
            };
            gestureDataListener.onRangeGestureStart = [&sideEffects]() {
                ++sideEffects;
            };
            testDataCsv(f, gestureDataListener);

            UNIT_ASSERT(triggered);
            UNIT_ASSERT(sideEffects == 0);
            triggered = false;
        }
    }

    Y_UNIT_TEST(testGestureVolumeUp)
    {
        GestureDataListener::Settings settings;
        settings.tofIsCalibrated = true;
        GestureDataListener gestureDataListener(settings);

        const std::string files[]{
            "volume_up/mp_calibrated_FF98F029E72264BA4792A68E_01.csv",
            "volume_up/mp_calibrated_FF98F029E72264BA4792A68E_01_with_0.csv"};

        for (auto f : files) {
            gestureDataListener.clearState();

            bool start = false;
            bool end = false;
            int sideEffects = 0;

            constexpr double volumeStart = 5.;
            double volume = volumeStart;
            double volumeMax = volumeStart;
            gestureDataListener.onRangeGestureStart = [&start]() {
                start = true;
            };
            gestureDataListener.onRangeGestureValue = [&volume, &volumeMax](double value) {
                volume += value;
                volumeMax = std::max(volumeMax, volume);
            };
            gestureDataListener.onRangeGestureEnd = [&end]() {
                end = true;
            };
            gestureDataListener.onLowHoldGesture = [&sideEffects]() {
                ++sideEffects;
            };
            testDataCsv(f, gestureDataListener);
            YIO_LOG_INFO("volume " << volume << ", volumeMax " << volumeMax);
            YIO_LOG_INFO("sideEffects " << sideEffects);
            UNIT_ASSERT(start);
            UNIT_ASSERT(end);
            UNIT_ASSERT(volume > volumeStart + 2.);
            UNIT_ASSERT(volume == volumeMax);
            UNIT_ASSERT(sideEffects == 0);
        }
    }

    Y_UNIT_TEST(testGestureActivate)
    {
        GestureDataListener::Settings settings;
        settings.tofIsCalibrated = true;
        GestureDataListener gestureDataListener(settings);

        const std::string files[]{
            "activation/mp_calibrated_FF98F029E72264BA4792A68E_121cm_lamp_01.csv",
            "activation/mp_calibrated_FF98F029E72264BA4792A68E_01.csv",
            "activation/mp_calibrated_FF98F029E72264BA4792A68E_02.csv",
            "activation/mp_calibrated_FF98F029E72264BA4792A68E_03.csv",
            "activation/mp_calibrated_FF98F029E72264BA4792A68E_04.csv"};

        for (auto f : files) {
            gestureDataListener.clearState();

            int start = 0;
            int end = 0;
            int penalty = 0;

            gestureDataListener.onRangeGestureStart = [&start]() {
                start++;
            };
            gestureDataListener.onRangeGestureEnd = [&end]() {
                end++;
            };

            gestureDataListener.onDoubleSwingGesture = [&penalty]() {
                penalty += 1;
            };
            gestureDataListener.onLowHoldGesture = [&penalty]() {
                penalty += 1;
            };
            gestureDataListener.onRangeGestureValue = [&penalty](double value) {
                penalty += gestureValueToPenalty(value);
            };

            testDataCsv(f, gestureDataListener);
            UNIT_ASSERT_VALUES_EQUAL(start, 1);
            UNIT_ASSERT_VALUES_EQUAL(end, 1);
            UNIT_ASSERT_VALUES_EQUAL(penalty, 0);
            YIO_LOG_INFO("testGestureActivate penalty " << penalty);
        }
    }

    Y_UNIT_TEST(testGestureVolumeDown) {
        GestureDataListener::Settings settings;
        settings.tofIsCalibrated = true;
        GestureDataListener gestureDataListener(settings);

        const std::string files[]{
            "volume_down/mp_calibrated_FF98F029E72264BA4792A68E_01.csv",
            "volume_down/mp_calibrated_FF98F029E72264BA4792A68E_01_with_0.csv"};

        for (auto f : files) {
            gestureDataListener.clearState();

            bool start = false;
            bool end = false;

            constexpr double volumeStart = 5.;
            double volume = volumeStart;
            double volumeMin = volumeStart;
            gestureDataListener.onRangeGestureStart = [&start]() {
                start = true;
            };
            gestureDataListener.onRangeGestureValue = [&volume, &volumeMin](double value) {
                volume += value;
                volumeMin = std::min(volumeMin, volume);
            };
            gestureDataListener.onRangeGestureEnd = [&end]() {
                end = true;
            };
            testDataCsv(f, gestureDataListener);
            YIO_LOG_INFO("volume " << volume << ", volumeMin " << volumeMin);
            UNIT_ASSERT(start);
            UNIT_ASSERT(end);
            UNIT_ASSERT(volume < volumeStart - 2.);
            UNIT_ASSERT(volume == volumeMin);
        }
    }
}
