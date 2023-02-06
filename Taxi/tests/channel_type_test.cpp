#include <gtest/gtest.h>

#include <models/postgresql/type_mappings.hpp>
#include <utils/exceptions.hpp>

namespace {
namespace dm = devicenotify::models;
}

TEST(DeviceNotifyChannels, Throw) {
  EXPECT_THROW(dm::ToChannelType("unknown_channel"),
               utils::exceptions::InternalException);
  EXPECT_THROW(dm::ToString(static_cast<dm::ChannelType>(
                   static_cast<int>(dm::ChannelType::kFCM) + 1)),
               utils::exceptions::InternalException);
}

TEST(DeviceNotifyChannels, StringToId) {
  std::vector<std::string> channel_names = {"fcm"};
  for (const auto& name : channel_names) {
    dm::ChannelType ct;
    std::string rev_name;
    EXPECT_NO_THROW(ct = dm::ToChannelType(name));
    EXPECT_NO_THROW(rev_name = dm::ToString(ct));
    EXPECT_EQ(name, rev_name);
  }
}

TEST(DeviceNotifyChannels, IdToString) {
  for (int value = 0; value <= static_cast<int>(dm::ChannelType::kFCM);
       ++value) {
    std::string name;
    dm::ChannelType rev_ct;
    EXPECT_NO_THROW(name = dm::ToString(static_cast<dm::ChannelType>(value)));
    EXPECT_NO_THROW(rev_ct = dm::ToChannelType(name));
    EXPECT_EQ(rev_ct, static_cast<dm::ChannelType>(value));
  }
}

TEST(DeviceNotifyChannels, Enumerator) {
  for (const auto& e :
       storages::postgres::io::CppToUserPg<dm::ChannelType>::enumerators) {
    std::string rev_name;
    dm::ChannelType rev_ct;
    EXPECT_GE(static_cast<int>(e.enumerator), 0);
    EXPECT_LE(e.enumerator, dm::ChannelType::kFCM);
    EXPECT_NO_THROW(rev_name = dm::ToString(e.enumerator));
    EXPECT_NO_THROW(rev_ct = dm::ToChannelType(std::string(e.literal)));
    EXPECT_EQ(rev_name, e.literal);
    EXPECT_EQ(rev_ct, e.enumerator);
  }
}
