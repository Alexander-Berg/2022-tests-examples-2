#include "counters.hpp"

#include <gtest/gtest.h>

TEST(PathCounters, Add) {
  models::PathCounters a{{"a", 1}, {"b", 2}, {"d", 6}};
  models::PathCounters b{{"a", 3}, {"c", 5}};
  models::Add(a, b);
  EXPECT_EQ(a, (models::PathCounters{{"a", 4}, {"b", 2}, {"c", 5}, {"d", 6}}));
}

TEST(PathCounters, Substract) {
  models::PathCounters a{{"a", 1}, {"b", 2}, {"d", 6}};
  models::PathCounters b{{"a", 3}, {"c", 5}};
  models::Substract(a, b);
  EXPECT_EQ(a,
            (models::PathCounters{{"a", -2}, {"b", 2}, {"c", -5}, {"d", 6}}));
}

TEST(PathCounters, Clamp) {
  models::PathCounters a{{"a", 1}, {"b", 2}, {"d", 6}, {"e", -1}};
  models::PathCounters b{{"a", 2}, {"c", 5}, {"d", 4}};
  models::Clamp(a, b);
  EXPECT_EQ(a, (models::PathCounters{
                   {"a", 2}, {"b", 2}, {"c", 5}, {"d", 6}, {"e", 0}}));
}

TEST(Counters, Add) {
  models::Counters a{{"path1", {{"a", 1}}}, {"path2", {{"a", 2}}}};
  models::Counters b{{"path1", {{"a", 3}}}, {"path3", {{"a", 4}}}};
  models::Add(a, b);
  EXPECT_EQ(a, (models::Counters{{"path1", {{"a", 4}}},
                                 {"path2", {{"a", 2}}},
                                 {"path3", {{"a", 4}}}}));
}

TEST(Counters, Substract) {
  models::Counters a{{"path1", {{"a", 1}}}, {"path2", {{"a", 2}}}};
  models::Counters b{{"path1", {{"a", 3}}}, {"path3", {{"a", 4}}}};
  models::Substract(a, b);
  EXPECT_EQ(a, (models::Counters{{"path1", {{"a", -2}}},
                                 {"path2", {{"a", 2}}},
                                 {"path3", {{"a", -4}}}}));
}

TEST(Counters, Clamp) {
  models::Counters a{{"path1", {{"a", 1}}}, {"path2", {{"a", -2}}}};
  models::Counters b{{"path1", {{"a", 3}}}, {"path3", {{"a", 4}}}};
  models::Clamp(a, b);
  EXPECT_EQ(a, (models::Counters{{"path1", {{"a", 3}}},
                                 {"path2", {{"a", 0}}},
                                 {"path3", {{"a", 4}}}}));
}
