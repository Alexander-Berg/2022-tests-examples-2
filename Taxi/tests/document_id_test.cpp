#include <gtest/gtest.h>

#include <helpers/document_id.hpp>

TEST(DocumentIdData, TrivialCase) {
  const std::string document_id = "order_id/products/refund/operation_id";

  const helpers::document_id::DocumentIdData id_data(document_id);

  ASSERT_EQ(id_data.order_id.GetUnderlying(), "order_id");
  ASSERT_EQ(id_data.type, helpers::types::ReceiptType::kProducts);
  ASSERT_EQ(id_data.is_refund, true);
  ASSERT_EQ(id_data.operation_id.GetUnderlying(), "operation_id");
}

TEST(DocumentIdData, TrivialCaseNonRefund) {
  const std::string document_id = "order_id/products//operation_id";

  const helpers::document_id::DocumentIdData id_data(document_id);

  ASSERT_EQ(id_data.order_id.GetUnderlying(), "order_id");
  ASSERT_EQ(id_data.type, helpers::types::ReceiptType::kProducts);
  ASSERT_EQ(id_data.is_refund, false);
  ASSERT_EQ(id_data.operation_id.GetUnderlying(), "operation_id");
}

TEST(DocumentIdData, MalformedDocument) {
  const std::string document_id = "order_id/products//operation_id/";
  try {
    const helpers::document_id::DocumentIdData id_data(document_id);
  } catch (const std::runtime_error& error) {
    ASSERT_EQ(
        std::string(error.what()),
        "Can't parse string = order_id/products//operation_id/ DocumentIdData");
  }
}
