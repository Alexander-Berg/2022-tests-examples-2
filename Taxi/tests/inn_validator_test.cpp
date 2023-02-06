#include <gtest/gtest.h>

#include <utils/validators/inn_validator.hpp>

TEST(InnValidator, ValidIndividualINN) {
  const std::string inn = "479753957665";
  ASSERT_TRUE(utils::validators::IsValidInn(inn));
}

TEST(InnValidator, ValidLegalEntityINN) {
  const std::string inn = "1984281335";
  ASSERT_TRUE(utils::validators::IsValidInn(inn));
}

TEST(InnValidator, InvalidIndividualINN) {
  const std::string inn = "479753954665";
  ASSERT_FALSE(utils::validators::IsValidInn(inn));
}

TEST(InnValidator, InvalidLegalEntityINN) {
  const std::string inn = "1984281835";
  ASSERT_FALSE(utils::validators::IsValidInn(inn));
}
