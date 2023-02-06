#include <userver/utest/utest.hpp>

#include <boost/range/irange.hpp>

#include <ranges/to_container.hpp>

namespace {

class Indicator {
 public:
  Indicator(int value) : value_(value){};

  Indicator(const Indicator&) = default;

  Indicator(Indicator&& other) {
    value_ = other.value_;
    other.value_ = std::nullopt;
  }

  std::optional<int> Value() const { return value_; }

 private:
  std::optional<int> value_;
};

}  // namespace

TEST(Ranges, CopyPipe) {
  const std::vector<Indicator> vector = {1, 2};

  const auto list = vector | ranges::ToList;

  ASSERT_EQ(2, list.size());
  EXPECT_EQ(1, list.begin()->Value());
  EXPECT_EQ(2, (++list.begin())->Value());

  EXPECT_EQ(1, vector[0].Value());
  EXPECT_EQ(2, vector[1].Value());
}

TEST(Ranges, MovePipe) {
  std::vector<Indicator> vector = {1, 2};

  const auto list = std::move(vector) | ranges::ToList;

  ASSERT_EQ(2, list.size());
  EXPECT_EQ(1, list.begin()->Value());
  EXPECT_EQ(2, (++list.begin())->Value());

  ASSERT_EQ(2, vector.size());
  EXPECT_EQ(std::nullopt, vector[0].Value());
  EXPECT_EQ(std::nullopt, vector[1].Value());
}

TEST(Ranges, FromGenerator) {
  const std::vector<int> expected = {1, 3, 5};
  const auto actual = boost::irange(1, 6, 2) | ranges::ToVector;
  ASSERT_EQ(expected, actual);
}
