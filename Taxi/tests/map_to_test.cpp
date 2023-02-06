#include <list>
#include <type_traits>
#include <vector>

#include <boost/range/irange.hpp>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <ranges/map_to.hpp>

namespace {

class Indicator {
 public:
  Indicator(int value) : value_(value){};
  Indicator(std::nullopt_t) : value_(std::nullopt){};

  Indicator(const Indicator&) = default;

  Indicator(Indicator&& other) noexcept {
    value_ = other.value_;
    other.value_ = std::nullopt;
  }

  std::optional<int> Value() const { return value_; }

  bool operator==(const Indicator& other) const {
    return value_ == other.value_;
  }

 private:
  std::optional<int> value_;
};

Indicator CopyIndicator(const Indicator& value) { return value; }

Indicator MoveIndicator(Indicator&& value) { return std::move(value); }

const auto ToString = [](auto value) { return std::to_string(value); };

}  // namespace

TEST(RangesMapTo, MapTo) {
  const std::vector<int> vector = {1, 2};

  const std::list<std::string> strings =
      vector | ranges::MapTo<std::list<std::string>>(ToString);

  EXPECT_THAT(vector, ::testing::ElementsAre(1, 2));
  EXPECT_THAT(strings, ::testing::ElementsAre("1", "2"));
}

TEST(RangesMapTo, MapToTemplate) {
  const std::vector<int> vector = {1, 2};

  const std::list<std::string> strings =
      vector | ranges::MapTo<std::list>(ToString);

  EXPECT_THAT(vector, ::testing::ElementsAre(1, 2));
  EXPECT_THAT(strings, ::testing::ElementsAre("1", "2"));
}

TEST(RangesMapTo, Map) {
  const std::vector<int> vector = {1, 2};

  const std::vector<std::string> strings = vector | ranges::Map(ToString);

  EXPECT_THAT(vector, ::testing::ElementsAre(1, 2));
  EXPECT_THAT(strings, ::testing::ElementsAre("1", "2"));
}

TEST(RangesMapTo, Copy) {
  const std::vector<Indicator> vector = {1, 2};

  const auto list = vector | ranges::MapTo<std::list>(CopyIndicator);

  EXPECT_THAT(vector, ::testing::ElementsAre(1, 2));
  EXPECT_THAT(list, ::testing::ElementsAre(1, 2));
}

TEST(RangesMapTo, Move) {
  std::vector<Indicator> vector = {1, 2};

  const auto list = std::move(vector) | ranges::MapTo<std::list>(MoveIndicator);

  EXPECT_THAT(vector, ::testing::ElementsAre(std::nullopt, std::nullopt));
  EXPECT_THAT(list, ::testing::ElementsAre(1, 2));
}

TEST(RangesMapTo, FromGenerator) {
  const auto vector =
      boost::irange(1, 6, 2) | ranges::MapTo<std::vector>(ToString);

  EXPECT_THAT(vector, ::testing::ElementsAre("1", "3", "5"));
}
