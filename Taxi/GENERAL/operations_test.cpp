#include <virtual-tariffs/models/operations.hpp>

#include <gtest/gtest.h>

#include <string>
#include <unordered_set>

namespace {
struct SomeStruct {
  static SomeStruct FromString(const std::string&) { return SomeStruct{}; }

  static std::string ToString(const SomeStruct&) { return "SomeStruct"; }

  bool operator>(const SomeStruct&) const { return false; }
};
}  // namespace

TEST(VirtualTariffs, TestContainsAll) {
  using namespace virtual_tariffs::models;

  EXPECT_TRUE(GetFunctorByName<std::unordered_set<std::string>>("ContainsAll",
                                                                {"1", "2", "3"})
                  ->Apply(std::unordered_set<std::string>{"1", "2", "3", "4"}));
  EXPECT_FALSE(GetFunctorByName<std::unordered_set<std::string>>(
                   "ContainsAll", {"1", "2", "3", "4"})
                   ->Apply(std::unordered_set<std::string>{"1", "2", "3"}));
  EXPECT_THROW(GetFunctorByName<SomeStruct>("ContainsAll", {""}),
               std::logic_error);
  EXPECT_TRUE(GetFunctorByName<std::string>("ContainsAll", {"4", "9"})
                  ->Apply(std::string("4.99")));
  EXPECT_FALSE(GetFunctorByName<std::string>("ContainsAll", {"4", "5"})
                   ->Apply(std::string("4.99")));
  EXPECT_THROW(GetFunctorByName<std::string>("ContainsAll", {"4.9"})
                   ->Apply(std::string("4.99")),
               std::invalid_argument);
}

TEST(VirtualTariffs, TestContainsOneOf) {
  using namespace virtual_tariffs::models;

  EXPECT_TRUE(GetFunctorByName<std::unordered_set<std::string>>("ContainsOneOf",
                                                                {"1", "4"})
                  ->Apply(std::unordered_set<std::string>{"1", "2", "3", "4"}));
  EXPECT_TRUE(
      GetFunctorByName<std::unordered_set<std::string>>("ContainsOneOf", {"1"})
          ->Apply(std::unordered_set<std::string>{"1", "2", "3", "4"}));
  EXPECT_FALSE(
      GetFunctorByName<std::unordered_set<std::string>>("ContainsOneOf", {"1"})
          ->Apply(std::unordered_set<std::string>{"2", "3"}));
  EXPECT_TRUE(GetFunctorByName<std::unordered_set<std::string>>("ContainsOneOf",
                                                                {"1", "2"})
                  ->Apply(std::unordered_set<std::string>{"2", "3"}));
  EXPECT_TRUE(GetFunctorByName<std::unordered_set<std::string>>("ContainsOneOf",
                                                                {"1", "2", "3"})
                  ->Apply(std::unordered_set<std::string>{"3"}));
}

TEST(VirtualTariffs, TestContainsNoOne) {
  using namespace virtual_tariffs::models;

  EXPECT_FALSE(
      GetFunctorByName<std::unordered_set<std::string>>("ContainsNoOne",
                                                        {"1", "4"})
          ->Apply(std::unordered_set<std::string>{"1", "2", "3", "4"}));
  EXPECT_FALSE(
      GetFunctorByName<std::unordered_set<std::string>>("ContainsNoOne", {"1"})
          ->Apply(std::unordered_set<std::string>{"1", "2", "3", "4"}));
  EXPECT_TRUE(
      GetFunctorByName<std::unordered_set<std::string>>("ContainsNoOne", {"1"})
          ->Apply(std::unordered_set<std::string>{"2", "3"}));
  EXPECT_FALSE(GetFunctorByName<std::unordered_set<std::string>>(
                   "ContainsNoOne", {"1", "2"})
                   ->Apply(std::unordered_set<std::string>{"2", "3"}));
  EXPECT_FALSE(GetFunctorByName<std::unordered_set<std::string>>(
                   "ContainsNoOne", {"1", "2", "3"})
                   ->Apply(std::unordered_set<std::string>{"3"}));
}

TEST(VirtualTariffs, TestNotContainsAll) {
  using namespace virtual_tariffs::models;

  EXPECT_FALSE(
      GetFunctorByName<std::unordered_set<std::string>>("NotContainsAll",
                                                        {"1", "2", "3"})
          ->Apply(std::unordered_set<std::string>{"1", "2", "3", "4"}));
  EXPECT_TRUE(GetFunctorByName<std::unordered_set<std::string>>(
                  "NotContainsAll", {"1", "2", "3", "4"})
                  ->Apply(std::unordered_set<std::string>{"1", "2", "3"}));
  EXPECT_THROW(GetFunctorByName<SomeStruct>("None", {""})->Apply(SomeStruct{}),
               std::logic_error);
  EXPECT_FALSE(GetFunctorByName<std::string>("NotContainsAll", {"4", "9"})
                   ->Apply(std::string("4.99")));
  EXPECT_TRUE(GetFunctorByName<std::string>("NotContainsAll", {"4", "5"})
                  ->Apply(std::string("4.99")));
}

TEST(VirtualTariffs, TestGreater) {
  using namespace virtual_tariffs::models;

  EXPECT_TRUE(GetFunctorByName<double>("Greater", {"4.9"})->Apply(5.0));
  EXPECT_TRUE(GetFunctorByName<std::string>("Greater", {"4.9"})
                  ->Apply(std::string("5.0")));
  EXPECT_FALSE(GetFunctorByName<double>("LessOrEqual", {"4.9"})->Apply(5.0));
  EXPECT_FALSE(GetFunctorByName<std::string>("LessOrEqual", {"4.9"})
                   ->Apply(std::string("5.0")));
  EXPECT_THROW(
      GetFunctorByName<std::unordered_set<std::string>>("Greater", {""}),
      std::logic_error);
  EXPECT_FALSE(
      GetFunctorByName<SomeStruct>("Greater", {""})->Apply(SomeStruct{}));
  EXPECT_TRUE(
      GetFunctorByName<SomeStruct>("LessOrEqual", {""})->Apply(SomeStruct{}));
}

TEST(VirtualTariffs, TestOperationNames) {
  using namespace virtual_tariffs::models::operations;

  auto name = Greater<std::unordered_set<std::string>, false>().Name();
  EXPECT_EQ(std::string("Base"), name);
  name = Greater<double, false>({"4.5"}).Name();
  EXPECT_EQ(std::string("Greater"), name);
  name = Greater<std::unordered_set<std::string>, true>().Name();
  EXPECT_EQ(std::string("Base"), name);
  name = Greater<double, true>({"4.5"}).Name();
  EXPECT_EQ(std::string("LessOrEqual"), name);
  EXPECT_EQ(Base().Name(), std::string("Base"));
  EXPECT_THROW(Base(std::vector<std::string>{}), std::logic_error);
}
