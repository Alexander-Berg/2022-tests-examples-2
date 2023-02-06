#include <gtest/gtest.h>
#include <userver/utest/utest.hpp>

#include "requirements_v2.hpp"

#include <filters/efficiency/fetch_tags/fetch_tags.hpp>
#include <filters/infrastructure/fetch_unique_driver/fetch_unique_driver.hpp>

namespace cf = candidates::filters;
namespace cfi = cf::infrastructure;
namespace cfe = cf::efficiency;

const cf::FilterInfo kEmptyInfo;

UTEST(RequirementsV2Filter, Sample) {
  models::UniqueDriver unique_driver;
  unique_driver.exams.Add("abc");

  cf::Context context;
  cfe::FetchTags::Set(context, {1, 2, 3});
  cfi::FetchUniqueDriver::Set(
      context,
      std::make_shared<const models::UniqueDriver>(std::move(unique_driver)));

  candidates::GeoMember driver;

  {
    cfi::RequirementsV2 filter{kEmptyInfo,
                               {{1}, {4}, models::drivers::Exams{}}};
    ASSERT_EQ(cf::Result::kAllow, filter.Process(driver, context));
  }

  {
    cfi::RequirementsV2 filter{kEmptyInfo,
                               {{1, 2, 3}, {}, models::drivers::Exams{"abc"}}};
    ASSERT_EQ(cf::Result::kAllow, filter.Process(driver, context));
  }

  {
    cfi::RequirementsV2 filter{kEmptyInfo, {{4}, {}, models::drivers::Exams{}}};
    ASSERT_EQ(cf::Result::kDisallow, filter.Process(driver, context));
  }

  {
    cfi::RequirementsV2 filter{kEmptyInfo, {{}, {1}, models::drivers::Exams{}}};
    ASSERT_EQ(cf::Result::kDisallow, filter.Process(driver, context));
  }

  {
    cfi::RequirementsV2 filter{kEmptyInfo,
                               {{}, {}, models::drivers::Exams{"qwe"}}};
    ASSERT_EQ(cf::Result::kDisallow, filter.Process(driver, context));
  }
}
