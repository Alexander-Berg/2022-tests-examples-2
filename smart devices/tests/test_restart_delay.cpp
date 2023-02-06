#include <smart_devices/tools/launcher2/lib/launcher.h>
#include <smart_devices/tools/launcher2/lib/utility.h>

#include <library/cpp/testing/unittest/registar.h>

Y_UNIT_TEST_SUITE(TRestartDelay) {

    Y_UNIT_TEST(Calculation) {
        std::chrono::seconds delay = restartDelay(5 /* baseRestartDelay in seconds */, 0 /* consequentRestartCount */);
        UNIT_ASSERT_GE(delay, std::chrono::seconds((int)(5 * (1 - JITTER_SHARE))));
        UNIT_ASSERT_LE(delay, std::chrono::seconds((int)(5 * (1 + JITTER_SHARE))));

        delay = restartDelay(5, 3);
        UNIT_ASSERT_GE(delay, std::chrono::seconds((int)(31 * (1 - JITTER_SHARE))));
        UNIT_ASSERT_LE(delay, std::chrono::seconds((int)(31 * (1 + JITTER_SHARE))));

        delay = restartDelay(5, 7);
        UNIT_ASSERT_GE(delay, std::chrono::seconds((int)(Launcher::MAX_RESTART_DELAY*(1 - JITTER_SHARE))));
        UNIT_ASSERT_LE(delay, std::chrono::seconds((int)(Launcher::MAX_RESTART_DELAY*(1 + JITTER_SHARE))));

        delay = restartDelay(5, 70);
        UNIT_ASSERT_GE(delay, std::chrono::seconds((int)(Launcher::MAX_RESTART_DELAY*(1 - JITTER_SHARE))));
        UNIT_ASSERT_LE(delay, std::chrono::seconds((int)(Launcher::MAX_RESTART_DELAY*(1 + JITTER_SHARE))));

        delay = restartDelay(5, 700);
        UNIT_ASSERT_GE(delay, std::chrono::seconds((int)(Launcher::MAX_RESTART_DELAY*(1 - JITTER_SHARE))));
        UNIT_ASSERT_LE(delay, std::chrono::seconds((int)(Launcher::MAX_RESTART_DELAY*(1 + JITTER_SHARE))));

        delay = restartDelay(0, 0);
        UNIT_ASSERT_EQUAL(delay, std::chrono::seconds(0));

        delay = restartDelay(0, 5);
        UNIT_ASSERT_EQUAL(delay, std::chrono::seconds(0));

        delay = restartDelay(0, 70);
        UNIT_ASSERT_EQUAL(delay, std::chrono::seconds(0));
    }
}
