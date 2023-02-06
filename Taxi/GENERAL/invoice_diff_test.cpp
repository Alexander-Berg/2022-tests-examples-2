#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <grocery-payments-shared/invoice.hpp>
#include <grocery-payments-shared/invoice_diff.hpp>

#include <clients/transactions/definitions.hpp>

namespace {

using clients::transactions::Item;
using clients::transactions::PaymentItems;
using clients::transactions::PaymentType;

template <class T>
struct ParamDiff {
  std::string name;
  std::vector<T> items1;
  std::vector<T> items2;
  std::vector<T> expected;
};

template <class T>
std::string PrintToString(const ParamDiff<T>& param) {
  return param.name;
}

Item MakeItem(const std::string& item_id, int amount = 100) {
  Item result;
  result.item_id = item_id;
  result.amount = amount;
  return result;
}

Item MakeItem(const std::string& item_id, int price, int quantity) {
  Item result;
  result.item_id = item_id;
  result.price = price;
  result.quantity = quantity;
  return result;
}

}  // namespace

namespace clients::transactions {

void PrintTo(const Item& value, std::ostream* os) {
  *os << '(' << value.item_id << ' ';
  if (value.amount) {
    *os << *value.amount;
  } else if (value.price && value.quantity) {
    *os << *value.price << 'x' << *value.quantity;
  }
  *os << ')';
}

void PrintTo(const PaymentItems& value, std::ostream* os) {
  *os << "(" << ToString(value.payment_type) << ": {";
  for (const auto& item : value.items) {
    PrintTo(item, os);
  }
  *os << "})";
}

}  // namespace clients::transactions

using namespace grocery_payments_shared;

class InvoiceDiffItems : public ::testing::TestWithParam<ParamDiff<Item>> {};

TEST_P(InvoiceDiffItems, Check) {
  const auto& param = GetParam();

  auto result = invoice::Diff(param.items1, param.items2);

  auto items1_amount = invoice::GetAmount(param.items1);
  auto items2_amount = invoice::GetAmount(param.items2);
  auto result_amount = invoice::GetAmount(result);

  EXPECT_THAT(result, ::testing::ElementsAreArray(param.expected));
  EXPECT_EQ(items1_amount, items2_amount + result_amount);
}

INSTANTIATE_TEST_SUITE_P(  //
    Test, InvoiceDiffItems,
    ::testing::Values(  //
        ParamDiff<Item>{
            "only_items1",
            /* items1 */
            {
                MakeItem("1", 10),
            },
            /* items2 */ {},
            /* expected */
            {
                MakeItem("1", 10),
            },
        },
        ParamDiff<Item>{
            "only_items2",
            /* items1 */ {},
            /* items2 */
            {
                MakeItem("1", 10),
            },
            /* expected */
            {
                MakeItem("1", -10),
            },
        },
        ParamDiff<Item>{
            "items1_and_items2",
            /* items1 */
            {
                MakeItem("1", 10),
                MakeItem("2", 10),
            },
            /* items2 */
            {
                MakeItem("1", 10),
                MakeItem("3", 10),
            },
            /* expected */
            {
                MakeItem("2", +10),
                MakeItem("3", -10),
            },
        },
        ParamDiff<Item>{
            "items1_and_items2_shuffle",
            /* items1 */
            {
                MakeItem("2", 10),
                MakeItem("1", 10),
            },
            /* items2 */
            {
                MakeItem("3", 10),
                MakeItem("1", 10),
            },
            /* expected */
            {
                MakeItem("2", +10),
                MakeItem("3", -10),
            },
        },
        ParamDiff<Item>{
            "skip_zero",
            /* items1 */
            {
                MakeItem("1", 0),
                MakeItem("2", 1),
                MakeItem("3", 0),
            },
            /* items2 */
            {
                MakeItem("1", 0),
                MakeItem("2", 0),
                MakeItem("3", 1),
            },
            /* expected */
            {
                MakeItem("2", +1),
                MakeItem("3", -1),
            },
        },
        ParamDiff<Item>{
            "diff_amount",
            /* items1 */
            {
                MakeItem("1", 10),
                MakeItem("2", 20),
            },
            /* items2 */
            {
                MakeItem("1", 20),
                MakeItem("2", 10),
            },
            /* expected */
            {
                MakeItem("1", -10),
                MakeItem("2", +10),
            },
        },
        ParamDiff<Item>{
            "diff_quantity",
            /* items1 */
            {
                MakeItem("1", 10, 1),
                MakeItem("2", 10, 2),
                MakeItem("3", 10, 3),
            },
            /* items2 */
            {
                MakeItem("1", 10, 2),
                MakeItem("2", 10, 1),
                MakeItem("3", 10, 3),
            },
            /* expected */
            {
                MakeItem("1", 10, -1),
                MakeItem("2", 10, +1),
            },
        },
        ParamDiff<Item>{
            "negate",
            /* items1 */ {},
            /* items2 */
            {
                MakeItem("1", 10),
                MakeItem("2", 20, 1),
            },
            /* expected */
            {
                MakeItem("1", -10),
                MakeItem("2", +20, -1),
            },
        },
        ParamDiff<Item>{
            "empty",
            /* items1 */ {},
            /* items2 */ {},
            /* expected */ {},
        }),
    ::testing::PrintToStringParamName());

class InvoiceDiffItemsByPaymentType
    : public ::testing::TestWithParam<ParamDiff<PaymentItems>> {};

TEST_P(InvoiceDiffItemsByPaymentType, Check) {
  const auto& param = GetParam();

  auto result = invoice::Diff(param.items1, param.items2);

  auto items1_amount = invoice::GetAmount(param.items1);
  auto items2_amount = invoice::GetAmount(param.items2);
  auto result_amount = invoice::GetAmount(result);

  EXPECT_THAT(result, ::testing::ElementsAreArray(param.expected));
  EXPECT_EQ(items1_amount, items2_amount + result_amount);
}

INSTANTIATE_TEST_SUITE_P(  //
    Test, InvoiceDiffItemsByPaymentType,
    ::testing::Values(  //
        ParamDiff<PaymentItems>{
            "only_items1",
            /* items1 */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {
                        MakeItem("1", 10),
                    },
                },
            },
            /* items2 */ {},
            /* expected */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {
                        MakeItem("1", 10),
                    },
                },
            },
        },
        ParamDiff<PaymentItems>{
            "only_items2",
            /* items1 */ {},
            /* items2 */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {
                        MakeItem("1", 10),
                    },
                },
            },
            /* expected */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {
                        MakeItem("1", -10),
                    },
                },
            },
        },
        ParamDiff<PaymentItems>{
            "items1_and_items2",
            /* items1 */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {
                        MakeItem("1", 10),
                        MakeItem("2", 10),
                    },
                },
            },
            /* items2 */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {
                        MakeItem("1", 10),
                        MakeItem("3", 10),
                    },
                },
            },
            /* expected */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {
                        MakeItem("2", +10),
                        MakeItem("3", -10),
                    },
                },
            },
        },
        ParamDiff<PaymentItems>{
            "different_payment_types",
            /* items1 */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {
                        MakeItem("1", 10),
                    },
                },
            },
            /* items2 */
            {
                PaymentItems{
                    PaymentType::kPersonalWallet,
                    {
                        MakeItem("1", 10),
                    },
                },
            },
            /* expected */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {
                        MakeItem("1", 10),
                    },
                },
                PaymentItems{
                    PaymentType::kPersonalWallet,
                    {
                        MakeItem("1", -10),
                    },
                },
            },
        },
        ParamDiff<PaymentItems>{
            "shuffle",
            /* items1 */
            {
                PaymentItems{
                    PaymentType::kPersonalWallet,
                    {},
                },
            },
            /* items2 */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {},
                },
            },
            /* expected */
            {
                PaymentItems{
                    PaymentType::kCard,
                    {},
                },
                PaymentItems{
                    PaymentType::kPersonalWallet,
                    {},
                },
            },
        },
        ParamDiff<PaymentItems>{
            "empty",
            /* items1 */ {},
            /* items2 */ {},
            /* expected */ {},
        }),
    ::testing::PrintToStringParamName());
