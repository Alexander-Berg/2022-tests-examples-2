#include <gtest/gtest.h>

#include <filters/infrastructure/fetch_final_classes/fetch_final_classes.hpp>
#include "class.hpp"

namespace cf = candidates::filters;
namespace cfi = candidates::filters::infrastructure;

namespace {

const cf::FilterInfo kEmptyInfo;

cf::Context CreateContext(const std::vector<std::string>& classes) {
  cf::Context context;
  cfi::FetchFinalClasses::Set(context, models::Classes{classes});
  return context;
}

}  // namespace

TEST(ClassFilter, Basic) {
  cfi::Class filter(kEmptyInfo, models::Classes{});
  {
    auto context = CreateContext({"econom"});
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
  }
  {
    auto context = CreateContext({});
    EXPECT_EQ(filter.Process({}, context), cf::Result::kDisallow);
  }
}

TEST(ClassFilter, Required) {
  cfi::Class filter(kEmptyInfo, models::Classes{"econom", "comfort"});
  {
    auto context = CreateContext({"econom", "vip"});
    EXPECT_EQ(filter.Process({}, context), cf::Result::kDisallow);
  }
  {
    auto context = CreateContext({"econom", "comfort"});
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
  }
  {
    auto context = CreateContext({"econom", "comfort", "vip"});
    EXPECT_EQ(filter.Process({}, context), cf::Result::kAllow);
  }
}
