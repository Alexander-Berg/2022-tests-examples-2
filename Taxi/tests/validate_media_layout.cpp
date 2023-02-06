#include <userver/utest/utest.hpp>

#include <blender/experiment_values.hpp>

namespace ev = blender::experiment_values;

TEST(ValidateMediaLayout, Simple) {
  ASSERT_NO_THROW(ev::ValidateMediaLayout({{2, 4}, {4, 4}}));
  ASSERT_NO_THROW(ev::ValidateMediaLayout({{2, 4}, {4, 2}, {4, 2}}));
}

TEST(ValidateMediaLayout, Overflow) {
  ASSERT_THROW(ev::ValidateMediaLayout({{2, 4}, {5, 4}}), std::runtime_error);
}

TEST(ValidateMediaLayout, Irregular) {
  ASSERT_THROW(ev::ValidateMediaLayout({{2, 4}, {2, 3}, {2, 4}}),
               std::runtime_error);
}
