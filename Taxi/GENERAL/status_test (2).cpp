#include <gtest/gtest.h>

#include "status.hpp"

TEST(Status, Convert) {
  EXPECT_EQ(models::Status::ToString(models::Status::Code::kBusy), "busy");
  EXPECT_EQ(models::Status::ToString(models::Status::Code::kFree), "free");
  EXPECT_ANY_THROW(models::Status::ToString(models::Status::Code::kUnknown));

  EXPECT_EQ(models::Status::FromString("busy"), models::Status::Code::kBusy);
  EXPECT_EQ(models::Status::FromString("free"), models::Status::Code::kFree);
  EXPECT_EQ(models::Status::FromString("unknown"),
            models::Status::Code::kUnknown);
}
