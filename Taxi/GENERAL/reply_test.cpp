#include "reply.hpp"

#include <gtest/gtest.h>
#include <logging/logger_compat.hpp>

using namespace redis;

TEST(Reply, IsUnusableInstanceErrorMASTERDOWN) {
  auto data = ReplyData::CreateError(
      "MASTERDOWN Link with MASTER is down and slave-serve-stale-data is set "
      "to 'no'.");
  EXPECT_TRUE(data.IsUnusableInstanceError());
}

TEST(Reply, IsUnusableInstanceErrorLOADING) {
  auto data =
      ReplyData::CreateError("LOADING Redis is loading the dataset in memory");
  EXPECT_TRUE(data.IsUnusableInstanceError());
}

TEST(Reply, IsUnusableInstanceErrorERR) {
  auto data = ReplyData::CreateError("ERR index out of range");
  EXPECT_FALSE(data.IsUnusableInstanceError());
}
