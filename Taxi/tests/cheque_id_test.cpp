#include <gtest/gtest.h>

#include <payture/payture_receipt_parser.hpp>

TEST(BuildChequeId, PaymentsDocument) {
  const std::string cheque_id = payture::BuildChequeId("210811-003377", "123");

  ASSERT_EQ(cheque_id, "210811-003377/123");
}

TEST(BuildChequeId, ResultTooLong) {
  try {
    const std::string cheque_id = payture::BuildChequeId(
        "eats_core_very_very_very_very_very_loooong_string", "220101-123456");
  } catch (const std::runtime_error& error) {
    ASSERT_EQ(std::string(error.what()),
              "Document id = "
              "eats_core_very_very_very_very_very_loooong_string/220101-123456 "
              "too long size=73, need 63 at most");
  }
}
