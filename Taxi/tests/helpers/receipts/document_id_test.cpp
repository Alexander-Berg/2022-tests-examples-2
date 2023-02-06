#include <gtest/gtest.h>

#include <exception>
#include <helpers/receipts/document_id.hpp>
#include <helpers/receipts/exceptions.hpp>

TEST(OperationsDocumentIdData, TrivialCase) {
  const std::string document_id = "order_id:products:refund:1";

  const helpers::receipts::DocumentIdData id_data(document_id);

  ASSERT_EQ(id_data.order_id, "order_id");
  ASSERT_EQ(id_data.type, helpers::types::ReceiptType::kProducts);
  ASSERT_EQ(id_data.is_refund, true);
  ASSERT_EQ(id_data.operation_id, 1);
}

TEST(OperationsDocumentIdData, TrivialCaseNonRefund) {
  const std::string document_id = "order_id:products::1";

  const helpers::receipts::DocumentIdData id_data(document_id);

  ASSERT_EQ(id_data.order_id, "order_id");
  ASSERT_EQ(id_data.type, helpers::types::ReceiptType::kProducts);
  ASSERT_EQ(id_data.is_refund, false);
  ASSERT_EQ(id_data.operation_id, 1);
}

TEST(OperationsDocumentIdData, MalformedDocument) {
  const std::string document_id = "order_id:products::1:";
  ASSERT_THROW(helpers::receipts::DocumentIdData id_data(document_id),
               helpers::receipts::DocumentIdException);
}
