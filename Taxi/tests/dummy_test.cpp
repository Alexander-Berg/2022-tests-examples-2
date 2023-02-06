#include <gtest/gtest.h>

#include "dummy.hpp"

TEST(DeviceNotify, Dummy) { EXPECT_TRUE(devicenotify::IsDummy()); }
