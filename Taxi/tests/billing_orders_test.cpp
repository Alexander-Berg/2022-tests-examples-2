#include <gtest/gtest.h>

#include <fstream>

#include <clients/billing_orders.hpp>
#include <common/test_config.hpp>
#include <config/config.hpp>

namespace {

const std::string kDirName = std::string(SOURCE_DIR) + "/tests/static/";

std::string ReadFile(const std::string& filename) {
  std::ifstream file(kDirName + filename);
  return std::string{std::istreambuf_iterator<char>(file),
                     std::istreambuf_iterator<char>()};
}

}  // namespace

TEST(TestBillingOrders, TestGeoareaActivity) {
  namespace bo = clients::billing_orders;

  const auto& response = ReadFile("billing_orders_doc.json");
  std::uint64_t doc_id;
  ASSERT_NO_THROW(doc_id = bo::ParseProcessEventResponse(response, {}));
  ASSERT_EQ(doc_id, 12345678910u);
}
