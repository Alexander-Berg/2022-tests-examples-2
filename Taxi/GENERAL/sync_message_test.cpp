#include "sync_message.hpp"

#include <gtest/gtest.h>

TEST(SyncMessage, Serialize) {
  {
    models::SyncMessage msg;
    const auto& data = models::SerializeSyncMessage(msg);
    const auto& parsed_msg = models::ParseSyncMessage(data);
    EXPECT_EQ(parsed_msg.counters, msg.counters);
    EXPECT_EQ(parsed_msg.limits_version, msg.limits_version);
    EXPECT_EQ(parsed_msg.lamport, msg.lamport);
  }
  {
    models::SyncMessage msg;
    msg.counters = {{"path1", {{"client1", 1}, {"client2", 2}}},
                    {"path2", {{"client3", 42}}},
                    {"path3", {}}};
    msg.lamport = 2;
    msg.limits_version = 42;
    const auto& data = models::SerializeSyncMessage(msg);
    const auto& parsed_msg = models::ParseSyncMessage(data);
    EXPECT_EQ(parsed_msg.counters, msg.counters);
    EXPECT_EQ(parsed_msg.limits_version, msg.limits_version);
    EXPECT_EQ(parsed_msg.lamport, msg.lamport);
  }
  {
    models::SyncMessage msg;
    msg.counters = {
        {"path1", {{"client1", 1}}},
        {"path2", {{"client1", 153}, {"client2", 2}}},
        {"path3", {{"client1", 11}, {"client33", 33}, {"client153", 37}}},
    };
    const auto& data = models::SerializeSyncMessage(msg);
    const auto& parsed_msg = models::ParseSyncMessage(data);
    EXPECT_EQ(msg.counters, parsed_msg.counters);
  }

  EXPECT_THROW(models::ParseSyncMessage("invalid data"), std::runtime_error);
}
