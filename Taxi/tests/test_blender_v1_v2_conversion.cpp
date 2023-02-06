#include <gtest/gtest.h>

#include <ml/blender/v1/objects.hpp>
#include <ml/blender/v2/objects.hpp>
#include <ml/common/filesystem.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("blender_v1");

TEST(BlenderV1V2Conversion, conversion) {
  auto state1 = ml::common::FromJsonString<ml::blender::v1::State>(
      ml::common::ReadFileContents(kTestDataDir + "/simple_state.json"));
  auto state2 = ml::common::FromJsonString<ml::blender::v2::State>(
      ml::common::ReadFileContents(kTestDataDir + "/simple_state.json"));

  ml::blender::v1::State state1_copy(state1);
  ml::blender::v2::State state21{};
  ml::blender::v2::DuckAssign(state1, state21);
  ASSERT_EQ(state21, state2);
  ASSERT_EQ(state1, state1_copy);

  ml::blender::v2::DuckAssign(std::move(state1_copy), state21);
  ASSERT_EQ(state21, state2);
  ASSERT_TRUE(state1 == state1_copy);  // state1 doesn't support move

  ml::blender::v2::State state2_copy(state2);
  ml::blender::v1::State state12{};
  ml::blender::v2::DuckAssign(state2, state12);
  ASSERT_EQ(state12, state1);
  ASSERT_EQ(state2, state2_copy);

  ml::blender::v2::DuckAssign(std::move(state2_copy), state12);
  ASSERT_EQ(state12, state1);
  ASSERT_FALSE(state2 == state2_copy);  // state2 does support move
}

}  // namespace
