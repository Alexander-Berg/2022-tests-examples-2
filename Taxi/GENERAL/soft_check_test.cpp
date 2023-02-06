#include <gtest/gtest.h>

#include "globus_soft_check_creator.hpp"

constexpr std::size_t kMaxTestGuidLength = 10;
using namespace eats_picker_orders::utils::soft_check;
using namespace eats_picker_orders::utils::soft_check::globus;

constexpr char GetNextDigit(char current_digit) {
  if ((current_digit >= '0' && current_digit < '9') ||
      (current_digit >= 'A' && current_digit < 'Z')) {
    return current_digit + 1;
  } else if (current_digit == '9') {
    return 'A';
  } else if (current_digit == 'Z') {
    return '0';
  }
  throw std::runtime_error("unreachable");
}

static_assert(GetNextDigit('0') == '1');
static_assert(GetNextDigit('9') == 'A');
static_assert(GetNextDigit('A') == 'B');
static_assert(GetNextDigit('Z') == '0');

TEST(GetId, GuidSize) {
  for (std::size_t i = 0; i < kMaxTestGuidLength; ++i) {
    ASSERT_EQ(GetId(i), std::string(i, '0'));
  }
}

TEST(GetId, Rotate) {
  const auto next_guid = GetId(std::string(kMaxTestGuidLength, 'Z'));
  ASSERT_EQ(std::string(kMaxTestGuidLength, '0'), next_guid);
}

TEST(GetId, Increment) {
  std::string next_guid = std::string(5, 'Z');

  char c1 = '0', c2 = '0', c3 = '0', c4 = '0', c5 = '0';
  do {
    do {
      do {
        do {
          do {
            next_guid = GetId(next_guid);
            ASSERT_EQ((std::string{c1, c2, c3, c4, c5}), next_guid);

            c5 = GetNextDigit(c5);
          } while (c5 != '0');
          c4 = GetNextDigit(c4);
        } while (c4 != '0');
        c3 = GetNextDigit(c3);
      } while (c3 != '0');
      c2 = GetNextDigit(c2);
    } while (c2 != '0');
    c1 = GetNextDigit(c1);
  } while (c1 != '0');
}
