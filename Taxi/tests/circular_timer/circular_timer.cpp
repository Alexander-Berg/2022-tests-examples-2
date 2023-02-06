#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <iostream>
#include <chrono>
#include <thread>

#include <taxi/tools/dorblu/lib/include/error.h>
#include <taxi/tools/dorblu/lib/include/circular_timer.h>

uint64_t getEpochMs(const std::chrono::system_clock::time_point& tp)
{
    auto tp_ms = std::chrono::time_point_cast<std::chrono::milliseconds>(tp);
    auto epoch = tp_ms.time_since_epoch();
    auto value = std::chrono::duration_cast<std::chrono::milliseconds>(epoch);
    return value.count();
}

TEST(CircularTimer, FilePointHistoryTest)
{
    FilePointHistory fph(5);

    auto now = std::chrono::system_clock::now();
    auto time = now;
    std::chrono::seconds timeDiff(5);

    fph.putPosition(time - 5 * timeDiff, 0);
    fph.putPosition(time - 4 * timeDiff, 2);
    fph.putPosition(time - 3 * timeDiff, 4);
    fph.putPosition(time - 2 * timeDiff, 6);
    fph.putPosition(time - timeDiff, 8);
    fph.putPosition(time, 10);

    /* Test 1: getting points */
    std::cout << "Retrieving data 5s ago: ";
    auto point = fph.position(5).point;
    EXPECT_EQ(static_cast<decltype(point)>(8), point);

    std::cout << "Retrieving data 6s ago: ";
    point = fph.position(7).point;
    EXPECT_EQ(static_cast<decltype(point)>(6), point);

    std::cout << "Retrieving data 60s ago: ";
    EXPECT_THROW(fph.position(60), DorBluError);
}
