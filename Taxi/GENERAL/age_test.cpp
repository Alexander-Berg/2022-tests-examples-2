#include <gtest/gtest.h>

#include "age.hpp"

using models::positions::MaxAge;
using std::chrono::seconds;
using MaxAgeZones = models::positions::MaxAgeConfig;
using MaxAgeClasses = MaxAgeZones::DictType::mapped_type;

const auto kMaxAgeConfig =
    MaxAgeZones{{},
                MaxAgeZones::DictType{
                    {{"__default__",
                      MaxAgeClasses{
                          {},
                          MaxAgeClasses::DictType{{
                              {"__default__", MaxAge{seconds{240}, seconds{0}}},
                              {"lavka", MaxAge{seconds{300}, seconds{300}}},
                              {"eda", MaxAge{seconds{240}, seconds{600}}},
                          }},
                      }}}}};

TEST(PositionsAge, GetGlobalMaxAge) {
  auto max_age = models::positions::GetGlobalMaxAge(kMaxAgeConfig);
  EXPECT_EQ(seconds{300}, max_age.value);
  EXPECT_EQ(seconds{540}, max_age.extension);  // (240 + 600) - 300;
}

TEST(PositionsAge, AgeChecker) {
  const auto now = std::chrono::system_clock::now();
  const auto checker =
      models::positions::AgeChecker{MaxAge{seconds{300}, seconds{300}}, now};

  EXPECT_TRUE(checker.IsValid());

  EXPECT_TRUE(checker.Check({now, now}));
  EXPECT_TRUE(checker.Check({now - seconds{200}, now}));
  EXPECT_TRUE(checker.Check({now - seconds{400}, now}));
  EXPECT_FALSE(checker.Check({now - seconds{700}, now}));
  EXPECT_TRUE(checker.Check({now - seconds{400}, now - seconds{200}}));
  EXPECT_FALSE(checker.Check({now - seconds{400}, now - seconds{400}}));
}
