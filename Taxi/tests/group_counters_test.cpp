
#include <gtest/gtest.h>

#include <couponcheck/helpers/group_counters.hpp>

namespace utils::helpers::test {

struct Group {
  std::string tariff;
  std::string payment_method;
  int value;
};

TEST(CheckGroupCounter, TariffOnly) {
  struct TestCase {
    std::vector<Group> groups;

    std::string tariff;
    int expected_value;
  };

  const std::vector<TestCase> tests = {
      {{{"econom", "card", 1}, {"econom", "cash", 1}}, "econom", 2},
      {{{"econom", "card", 1}, {"econom", "", 1}}, "econom", 2},
      {{{"econom", "card", 1}, {"econom", "", 1}}, "velosiped", 0},
  };

  for (const auto& test_ : tests) {
    ::utils::helpers::GroupCounter c;
    for (const auto& group : test_.groups)
      c.Insert(group.tariff, group.payment_method, group.value);

    EXPECT_EQ(c.GetByTariff(test_.tariff), test_.expected_value);
  }
}

TEST(CheckGroupCounter, PaymentTypeOnly) {
  struct TestCase {
    std::vector<Group> groups;

    std::string payment_type;
    int expected_value;
  };

  const std::vector<TestCase> tests = {
      {{{"econom", "card", 1}, {"econom", "cash", 1}, {"econom", "qqq", 1}},
       "card",
       1},
      {{{"econom", "card", 1}, {"econom", "", 1}}, "card", 1},
      {{{"econom", "cash", 1}, {"econom", "cash", 1}}, "cash", 1},
      {{{"econom", "cash", 1}, {"comfort", "cash", 1}}, "cash", 2},
      {{{"econom", "cash", 1}, {"comfort", "cash", 1}}, "KARD", 0},
  };

  for (const auto& test_ : tests) {
    ::utils::helpers::GroupCounter c;
    for (const auto& group : test_.groups)
      c.Insert(group.tariff, group.payment_method, group.value);

    EXPECT_EQ(c.GetByPaymentType(test_.payment_type), test_.expected_value);
  }
}

TEST(CheckGroupCounter, TariffAndPaymentMethod) {
  struct TestCase {
    std::vector<Group> groups;

    std::string tariff;
    std::string payment_method;
    int expected_value;
  };

  const std::vector<TestCase> tests = {
      {{{"econom", "card", 1}}, "econom", "card", 1},
      {{{"econom", "", 1}}, "econom", "card", 0},
      {{{"", "card", 1}}, "econom", "card", 0},
      {{{"", "card", 1}}, "", "card", 1},
      {{{"econom", "card", 1}}, "", "card", 0},
  };

  for (const auto& test_ : tests) {
    ::utils::helpers::GroupCounter c;
    for (const auto& group : test_.groups)
      c.Insert(group.tariff, group.payment_method, group.value);

    EXPECT_EQ(c.Get(test_.tariff, test_.payment_method), test_.expected_value);
  }
}

}  // namespace utils::helpers::test
