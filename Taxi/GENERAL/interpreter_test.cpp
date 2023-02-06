#include <gtest/gtest.h>

#include <netinet/in.h>
#include <cmath>

#include <interpreter/interpreter.hpp>
#include <models/serialization/helpers.hpp>

namespace {

using price_calc::interpreter::Bytecode;
using price_calc::interpreter::Info;
using price_calc::interpreter::Infos;
using price_calc::interpreter::Metadata;
using price_calc::interpreter::TripDetails;
using price_calc::models::Price;
using std::literals::string_literals::operator""s;

static const TripDetails kDefaultTripDetails(
    1,                        // total_distance
    std::chrono::seconds(1),  // total_time
    std::chrono::seconds(1),  // waiting_time
    std::chrono::seconds(0),  // waiting_in_transit_time
    std::chrono::seconds(0),  // waiting_in_destination_time
    {},                       // user_options
    {}                        // user_meta
);

void ExpectEqual(const Price& actual, const Price& expected) {
  EXPECT_DOUBLE_EQ(actual.boarding, expected.boarding);
  EXPECT_DOUBLE_EQ(actual.distance, expected.distance);
  EXPECT_DOUBLE_EQ(actual.time, expected.time);
  EXPECT_DOUBLE_EQ(actual.waiting, expected.waiting);
  EXPECT_DOUBLE_EQ(actual.requirements, expected.requirements);
  EXPECT_DOUBLE_EQ(actual.transit_waiting, expected.transit_waiting);
  EXPECT_DOUBLE_EQ(actual.destination_waiting, expected.destination_waiting);
}

void ExpectEqual(const Infos& actual, const Infos& expected) {
  EXPECT_EQ(actual.size(), expected.size());
  for (size_t i = 0; i < actual.size(); ++i) {
    ExpectEqual(actual[i].delta, expected[i].delta);
    EXPECT_EQ(actual[i].error, expected[i].error);
  }
}

void ExpectEqual(const Metadata& actual, const Metadata& expected) {
  EXPECT_EQ(actual.size(), expected.size());
  for (const auto& [k, v] : expected) {
    EXPECT_TRUE(actual.count(k));
    EXPECT_DOUBLE_EQ(actual.at(k), v);
  }
}

union DoubleBytes {
  double number;
  uint64_t lv;
  uint8_t bytes[sizeof(double)];
};

Bytecode DoubleToBytecode(double d) {
  DoubleBytes nb;
  nb.number = d;

  price_calc::models::serialization::NativeToBigInplace(
      nb.bytes, nb.bytes + sizeof(nb.bytes));

  std::vector<uint8_t> bc(nb.bytes, nb.bytes + sizeof(double));
  bc.insert(bc.begin(), 0x11);
  return bc;
}

}  // namespace

TEST(CompositePrice, SplitPrice) {
  Price input(30.0, 500.0, 450.0, 20.0, 0.0, 0.0, 0.0);
  Price expect(31.5, 525.0, 472.5, 21.0, 0.0, 0.0, 0.0);
  double price = 1050.0;
  const auto output = input.Split(price);
  ExpectEqual(output, expect);

  Price input1(100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
  Price expect1(105.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
  double price1 = 105.0;
  const auto output1 = input1.Split(price1);

  ExpectEqual(output1, expect1);
}

class CompositePriceArgs
    : public ::testing::TestWithParam<std::tuple<uint8_t, double>> {};

TEST_P(CompositePriceArgs, AdditionalArgs) {
  const auto [byte, ans] = GetParam();

  Price input(1, 0, 0, 0, 0, 0, 0);
  TripDetails trip_details(
      11,                        // total_distance
      std::chrono::seconds(22),  // total_time
      std::chrono::seconds(33),  // waiting_time
      std::chrono::seconds(44),  // waiting_in_transit_time
      std::chrono::seconds(55),  // waiting_in_destination_time
      {},                        // user_options
      {}                         // user_meta
  );

  Bytecode bc = {0x12, byte, 0x80};
  price_calc::utils::InputCodeStream code(bc);
  Price output =
      std::get<0>(price_calc::interpreter::Run(input, trip_details, {}, code));
  Price expect = input.Split(ans);
  ExpectEqual(output, expect);
}
INSTANTIATE_TEST_SUITE_P(CompositePriceArgs, CompositePriceArgs,
                         ::testing::Values(std::make_tuple(0x00, 11),
                                           std::make_tuple(0x01, 22),
                                           std::make_tuple(0x02, 33),
                                           std::make_tuple(0x03, 44),
                                           std::make_tuple(0x04, 55)));

TEST(CompositePrice, TotalPrice) {
  Price input(1, 2, 3, 4, 5, 6, 7);
  Bytecode bc = {0x13, 0x80};
  price_calc::utils::InputCodeStream code(bc);
  Price output = std::get<0>(price_calc::interpreter::Run(
      input, kDefaultTripDetails, {{0x01, "hello"}}, code));
  Price expect = input.Split(28);
  ExpectEqual(output, expect);
}

class CompositePriceInput
    : public ::testing::TestWithParam<std::tuple<uint8_t, double>> {};

TEST_P(CompositePriceInput, InputPrice) {
  const auto [byte, component_number] = GetParam();

  Price input(1, 2, 3, 4, 5, 6, 7);
  Bytecode bc = {0x14, byte, 0x80};
  price_calc::utils::InputCodeStream code(bc);
  Price output = std::get<0>(price_calc::interpreter::Run(
      input, kDefaultTripDetails, {{0x01, "hello"}}, code));
  Price expect = input.Split(component_number);
  ExpectEqual(output, expect);
}
INSTANTIATE_TEST_SUITE_P(
    CompositePriceInput, CompositePriceInput,
    ::testing::Values(std::make_tuple(0x00, 1), std::make_tuple(0x01, 2),
                      std::make_tuple(0x02, 3), std::make_tuple(0x03, 4),
                      std::make_tuple(0x04, 5), std::make_tuple(0x05, 6),
                      std::make_tuple(0x06, 7)));

// a, b, byte of operation, answer
class BinaryDoubleOperation : public ::testing::TestWithParam<
                                  std::tuple<double, double, uint8_t, double>> {
};

TEST_P(BinaryDoubleOperation, BinaryDouble) {  // 0x2?
  const auto [a, b, byte, ans] = GetParam();

  Price input(1, 0, 0, 0, 0, 0, 0);
  Bytecode bc_a = DoubleToBytecode(a);
  Bytecode bc_b = DoubleToBytecode(b);

  Bytecode bc;
  bc.insert(bc.end(), bc_a.begin(), bc_a.end());
  bc.insert(bc.end(), bc_b.begin(), bc_b.end());
  bc.push_back(byte);
  bc.push_back(0x80);
  price_calc::utils::InputCodeStream code(bc);
  Price output = std::get<Price>(price_calc::interpreter::Run(
      input, kDefaultTripDetails, {{0x01, "hello"}}, code));
  Price expect = input.Split(ans);
  ExpectEqual(output, expect);
}

INSTANTIATE_TEST_SUITE_P(BinaryDoubleOperation, BinaryDoubleOperation,
                         ::testing::Values(std::make_tuple(2, 3, 0x20, 5),
                                           std::make_tuple(2, 3, 0x21, -1),
                                           std::make_tuple(2, 3, 0x22, 6),
                                           std::make_tuple(10, 5, 0x23, 2),
                                           std::make_tuple(2, 3, 0x24, 8)));

class UnaryOperation
    : public ::testing::TestWithParam<std::tuple<double, uint8_t, double>> {};

TEST_P(UnaryOperation, UnaryDouble) {  // 0x3?, 0x4?
  const auto [a, byte, ans] = GetParam();

  Price input(1, 0, 0, 0, 0, 0, 0);
  Bytecode bc_a = DoubleToBytecode(a);

  Bytecode bc;
  bc.insert(bc.end(), bc_a.begin(), bc_a.end());
  bc.push_back(byte);
  bc.push_back(0x80);
  price_calc::utils::InputCodeStream code(bc);
  Price output = std::get<0>(price_calc::interpreter::Run(
      input, kDefaultTripDetails, {{0x01, "hello"}}, code));
  Price expect = input.Split(ans);
  ExpectEqual(output, expect);
}

INSTANTIATE_TEST_SUITE_P(
    UnaryOperation, UnaryOperation,
    ::testing::Values(
        std::make_tuple(3, 0x30, -3),
        std::make_tuple(2, 0x31, 7.3890560989306504),
        std::make_tuple(std::exp(1), 0x32, 1), std::make_tuple(4, 0x33, 2),
        std::make_tuple(M_PI / 2, 0x34, 1), std::make_tuple(M_PI, 0x35, -1),
        std::make_tuple(M_PI / 4, 0x36, 1), std::make_tuple(M_PI / 4, 0x37, 1),
        std::make_tuple(M_PI, 0x38, -1), std::make_tuple(M_PI / 2, 0x39, 1),
        std::make_tuple(0, 0x3A, 0), std::make_tuple(1, 0x3B, 0),
        std::make_tuple(0, 0x3C, 0), std::make_tuple(0, 0x3D, M_PI / 2),
        std::make_tuple(1, 0x3E, 0),
        std::make_tuple(1, 0x3F, 1.5707963267948966),

        std::make_tuple(0, 0x40, 0), std::make_tuple(0, 0x41, 1),
        std::make_tuple(INFINITY, 0x42, 1),
        std::make_tuple(1, 0x43, 1.3130352854993315),
        std::make_tuple(1, 0x44, 0.64805427366388546),
        std::make_tuple(1, 0x45, 0.85091812823932156)));

class CompareDoubleOperation : public ::testing::TestWithParam<
                                   std::tuple<double, double, uint8_t, bool>> {
};

TEST_P(CompareDoubleOperation, CompareDouble) {  // 0x5?
  const auto [a, b, byte, ans] = GetParam();

  Price input(1, 0, 0, 0, 0, 0, 0);
  Bytecode bc_false = DoubleToBytecode(-1);
  Bytecode bc_true = DoubleToBytecode(1);
  Bytecode bc_a = DoubleToBytecode(a);
  Bytecode bc_b = DoubleToBytecode(b);

  Bytecode bc;
  bc.insert(bc.end(), bc_a.begin(), bc_a.end());
  bc.insert(bc.end(), bc_b.begin(), bc_b.end());
  bc.push_back(byte);
  bc.insert(bc.end(), bc_true.begin(), bc_true.end());
  bc.insert(bc.end(), bc_false.begin(), bc_false.end());
  bc.push_back(0x00);
  bc.push_back(0x80);
  price_calc::utils::InputCodeStream code(bc);
  Price output = std::get<0>(price_calc::interpreter::Run(
      input, kDefaultTripDetails, {{0x01, "hello"}}, code));
  Price expect = input.Split(ans ? 1 : -1);
  ExpectEqual(output, expect);
}

INSTANTIATE_TEST_SUITE_P(CompareDoubleOperation, CompareDoubleOperation,
                         ::testing::Values(std::make_tuple(2, 3, 0x50, false),
                                           std::make_tuple(2, 3, 0x51, true),
                                           std::make_tuple(3, 3, 0x52, true),
                                           std::make_tuple(4, 5, 0x53, true)));

class BinaryBoolOperation
    : public ::testing::TestWithParam<std::tuple<bool, bool, uint8_t, bool>> {};

TEST_P(BinaryBoolOperation, CompareBool) {  // 0x6?
  const auto [a, b, byte, ans] = GetParam();

  Price input(1, 0, 0, 0, 0, 0, 0);
  Bytecode bc_false = DoubleToBytecode(-1);
  Bytecode bc_true = DoubleToBytecode(1);
  Bytecode bc_5 = DoubleToBytecode(5);
  Bytecode bc_4 = DoubleToBytecode(4);

  Bytecode bc;
  if (a) {  // ret_val = true
    bc.insert(bc.end(), bc_5.begin(), bc_5.end());
    bc.insert(bc.end(), bc_4.begin(), bc_4.end());
    bc.push_back(0x50);
  } else {  // ret_val = false
    bc.insert(bc.end(), bc_5.begin(), bc_5.end());
    bc.insert(bc.end(), bc_4.begin(), bc_4.end());
    bc.push_back(0x51);
  }
  if (b) {  // ret_val = true
    bc.insert(bc.end(), bc_5.begin(), bc_5.end());
    bc.insert(bc.end(), bc_4.begin(), bc_4.end());
    bc.push_back(0x50);
  } else {  // ret_val = false
    bc.insert(bc.end(), bc_5.begin(), bc_5.end());
    bc.insert(bc.end(), bc_4.begin(), bc_4.end());
    bc.push_back(0x51);
  }
  bc.push_back(byte);
  bc.insert(bc.end(), bc_true.begin(), bc_true.end());
  bc.insert(bc.end(), bc_false.begin(), bc_false.end());
  bc.push_back(0x00);
  bc.push_back(0x80);
  price_calc::utils::InputCodeStream code(bc);
  Price output = std::get<0>(price_calc::interpreter::Run(
      input, kDefaultTripDetails, {{0x01, "hello"}}, code));
  Price expect = input.Split(ans ? 1 : -1);
  ExpectEqual(output, expect);
}

INSTANTIATE_TEST_SUITE_P(
    BinaryBoolOperation, BinaryBoolOperation,
    ::testing::Values(std::make_tuple(true, true, 0x60, true),
                      std::make_tuple(true, false, 0x60, false),
                      std::make_tuple(true, false, 0x61, true),
                      std::make_tuple(true, false, 0x62, false),
                      std::make_tuple(true, false, 0x63, true)));

TEST(UnaryBoolOperation, NegateBool) {  // 0x70
  Price input(1, 0, 0, 0, 0, 0, 0);
  Bytecode bc_false = DoubleToBytecode(-1);
  Bytecode bc_true = DoubleToBytecode(1);
  Bytecode bc_5 = DoubleToBytecode(5);
  Bytecode bc_4 = DoubleToBytecode(4);

  Bytecode bc;
  bc.insert(bc.end(), bc_5.begin(), bc_5.end());
  bc.insert(bc.end(), bc_4.begin(), bc_4.end());
  bc.push_back(0x50);
  bc.push_back(0x70);
  bc.insert(bc.end(), bc_true.begin(), bc_true.end());
  bc.insert(bc.end(), bc_false.begin(), bc_false.end());
  bc.push_back(0x00);
  bc.push_back(0x80);
  price_calc::utils::InputCodeStream code(bc);
  Price output = std::get<0>(price_calc::interpreter::Run(
      input, kDefaultTripDetails, {{0x01, "hello"}}, code));
  Price expect = input.Split(-1);
  ExpectEqual(output, expect);
}

TEST(Interpreter, ReturnTotal) {  // 0x80, 0x81
  Bytecode bc0x80 = {0x11, 0x00, 0x00, 0x00, 0xC0,
                     0x94, 0x9B, 0xD1, 0x3F, 0x80};
  price_calc::utils::InputCodeStream code0x80(bc0x80);
  Price input(100, 0, 0, 0, 0, 0, 0);
  Price output0x80 = std::get<0>(price_calc::interpreter::Run(
      input, kDefaultTripDetails, {{0x01, "hello"}}, code0x80));
  Price expect = input.Split(4.0865501590595424e-312);
  ExpectEqual(output0x80, expect);

  Bytecode bc0x81 = {0x11, 0x00, 0x00, 0x00, 0xC0, 0x94, 0x9B, 0xD1, 0x3F, 0x11,
                     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x00,
                     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00,
                     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00,
                     0x00, 0x00, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x00,
                     0x00, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00,
                     0x00, 0x00, 0x00, 0x81};
  price_calc::utils::InputCodeStream code0x81(bc0x81);
  Price output0x81 = std::get<0>(price_calc::interpreter::Run(
      input, kDefaultTripDetails, {{0x01, "hello"}}, code0x81));
  Price expect0x81(4.0865501590595424e-312, 0, 0, 0, 0, 0, 0);
  ExpectEqual(output0x81, expect0x81);
}

// bytecode, price to split, errors
class RunBulkTest : public ::testing::TestWithParam<
                        std::tuple<Bytecode, double, Infos, Metadata>> {};

TEST_P(RunBulkTest, RunBulk) {
  const auto [bytecode, expected_sum_price, expected_infos, expected_meta] =
      GetParam();
  Price input(1, 2, 3, 4, 5, 6, 7);
  TripDetails trip_details(
      2800,                     // total_distance
      std::chrono::seconds(1),  // total_time
      std::chrono::seconds(1),  // waiting_time
      std::chrono::seconds(0),  // waiting_in_transit_time
      std::chrono::seconds(0),  // waiting_in_destination_time
      {},                       // user_options
      {}                        // user_meta
  );

  const auto [_, price, infos, meta] = price_calc::interpreter::RunBulk(
      input, trip_details, bytecode, 1.0, {{"hello", 0x01}});
  Price expected_price = input.Split(expected_sum_price);
  ExpectEqual(price, expected_price);
  ExpectEqual(infos, expected_infos);
  ExpectEqual(meta, expected_meta);
}

INSTANTIATE_TEST_SUITE_P(
    RunBulkTest, RunBulkTest,
    ::testing::Values(
        std::make_tuple(
            Bytecode{0x12, 0x00, 0x80, 0x14, 0x01, 0x80}, 200,
            Infos{{Price(99, 198, 297, 396, 495, 594, 693), std::nullopt},
                  {Price(-92.857142857142861, -185.71428571428572,
                         -278.57142857142856, -371.42857142857144,
                         -464.28571428571428, -557.14285714285711, -650),
                   std::nullopt}},
            Metadata{}),
        std::make_tuple(Bytecode{0x12, 0x99, 0x80, 0x14, 0x01, 0x80}, 2,
                        Infos{{Price(), "Invalid format of bytecode."s},
                              {Price(-0.9285714285714286, -1.8571428571428572,
                                     -2.7857142857142856, -3.7142857142857144,
                                     -4.6428571428571432, -5.5714285714285712,
                                     -6.5),
                               std::nullopt}},
                        Metadata{}),
        std::make_tuple(Bytecode{0x12, 0x00, 0x99, 0x80}, 28,
                        Infos{{Price(), "Unknown byte in bytecode."s}},
                        Metadata{}),
        std::make_tuple(Bytecode{0x12, 0x00}, 28,
                        Infos{{Price(), "No return byte."s}}, Metadata{}),
        std::make_tuple(Bytecode{0x14, 0x00, 0x80}, 1,
                        Infos{{Price(-0.9642857142857143, -1.9285714285714286,
                                     -2.8928571428571428, -3.8571428571428572,
                                     -4.8214285714285712, -5.7857142857142856,
                                     -6.75),
                               std::nullopt}},
                        Metadata{}),
        std::make_tuple(Bytecode{0x13, 0x80}, 28,
                        Infos{{Price(), std::nullopt}}, Metadata{}),
        std::make_tuple(Bytecode{0x14, 0x00, 0x14, 0x01, 0x14, 0x02, 0x14, 0x03,
                                 0x16, 0x00, 0x0b, 0x70, 0x61, 0x69, 0x64, 0x5f,
                                 0x6f, 0x70, 0x74, 0x69, 0x6f, 0x6e, 0x12, 0x05,
                                 0x90, 0x12, 0x05, 0x16, 0x00, 0x0b, 0x70, 0x61,
                                 0x69, 0x64, 0x5f, 0x6f, 0x70, 0x74, 0x69, 0x6f,
                                 0x6e, 0x91, 0x11, 0x40, 0x45, 0x00, 0x00, 0x00,
                                 0x00, 0x00, 0x00, 0x22, 0x14, 0x04, 0x00, 0x14,
                                 0x05, 0x14, 0x06, 0x81},
                        28, Infos{{Price(), std::nullopt}}, Metadata{}),
        std::make_tuple(Bytecode{0x13, 0x82, 0x00, 0x01, 0x15, 0x01, 0x80}, 28,
                        Infos{{Price(), std::nullopt}}, Metadata{}),
        std::make_tuple(Bytecode{0x13, 0x82, 0x00, 0x01, 0x15, 0x01, 0x83, 0x00,
                                 0x01, 0x15, 0x01, 0x80},
                        28, Infos{{Price(), std::nullopt}},
                        Metadata{{"hello", 28}}),
        std::make_tuple(Bytecode{0x13, 0x82, 0x00, 0x01, 0x17, 0x00, 0x01, 0x83,
                                 0x00, 0x01, 0x17, 0x00, 0x01, 0x80},
                        28, Infos{{Price(), std::nullopt}},
                        Metadata{{"hello", 28}}),
        std::make_tuple(Bytecode{0x13, 0x82, 0x00, 0x01, 0x14, 0x00, 0x14,
                                 0x01, 0x50, 0x18, 0x17, 0x00, 0x01, 0x00,
                                 0x83, 0x00, 0x01, 0x17, 0x00, 0x01, 0x80},
                        28, Infos{{Price(), std::nullopt}},
                        Metadata{{"hello", 28}}),
        std::make_tuple(Bytecode{0x13, 0x82, 0x00, 0x01, 0x14, 0x00, 0x14,
                                 0x01, 0x51, 0x18, 0x17, 0x00, 0x01, 0x00,
                                 0x83, 0x00, 0x01, 0x17, 0x00, 0x01, 0x80},
                        28, Infos{{Price(), std::nullopt}}, Metadata{})));

class ExceptionTest
    : public ::testing::TestWithParam<std::tuple<Bytecode, Infos>> {};

TEST_P(ExceptionTest, Exceptions) {
  const auto [bytecode, expected_infos] = GetParam();

  Price input(0, 0, 0, 0, 0, 0, 0);
  double ans = 0;

  const auto [_, price, infos, meta] = price_calc::interpreter::RunBulk(
      input, kDefaultTripDetails, bytecode, 1.0, {});
  Price expected_price = input.Split(ans);
  ExpectEqual(price, expected_price);
  ExpectEqual(infos, expected_infos);
  ExpectEqual(meta, {});
}

INSTANTIATE_TEST_SUITE_P(
    ExceptionTest, ExceptionTest,
    ::testing::Values(
        std::make_tuple(Bytecode{0x00},
                        Infos{{Price(), "Not enough arguments in stack."s}}),
        std::make_tuple(Bytecode{0x13}, Infos{{Price(), "No return byte."s}}),
        std::make_tuple(Bytecode{0x13, 0x87},
                        Infos{{Price(), "Unknown byte in bytecode."s}}),
        std::make_tuple(Bytecode{0x13, 0x13, 0x80},
                        Infos{{Price(), "Stack is not empty after return."s}}),
        std::make_tuple(Bytecode{0x15, 0x01, 0x80},
                        Infos{
                            {Price(), "Temporary value 1 does not exist."s}})));

TEST(Interpreter, GlobalUsage) {
  using price_calc::models::Operation;
  {
    Bytecode bytecode = Bytecode{0x11, 0x40, 0x5E, 0xDD, 0x2F, 0x1A, 0x9F, 0xBE,
                                 0x77, 0x85, 0x00, 0x01, 0x11, 0x00, 0x00, 0x00,
                                 0x00, 0x00, 0x00, 0x00, 0x00, 0x80};
    price_calc::utils::InputCodeStream code(bytecode);
    Price input(100, 0, 0, 0, 0, 0, 0);
    std::unordered_map<std::uint16_t, price_calc::interpreter::Value> globals;
    price_calc::interpreter::Run(input, kDefaultTripDetails, {}, code, globals);
    ASSERT_TRUE(std::holds_alternative<double>(globals.at(1)));
    ASSERT_EQ(std::get<double>(globals.at(1)), 123.456);
  }

  {
    Bytecode bytecode = Bytecode{0x19, 0x12, 0x34, 0x80};
    price_calc::utils::InputCodeStream code(bytecode);
    Price input(1, 1, 1, 1, 1, 1, 1);
    std::unordered_map<std::uint16_t, price_calc::interpreter::Value> globals{
        {0x1234, 1050.0}};
    auto result = std::get<0>(price_calc::interpreter::Run(
        input, kDefaultTripDetails, {}, code, globals));
    ASSERT_EQ(result.GetTotalPrice(), 1050);
  }
}

TEST(Interpreter, IsNull) {
  using price_calc::models::Operation;
  {
    Bytecode bytecode = Bytecode{
        0x11, 0x40, 0x5E, 0xDD, 0x2F, 0x1A, 0x9F, 0xBE, 0x77, 0x54, 0x85, 0x00,
        0x00, 0x16, 0x0,  0x0,  0x54, 0x85, 0x00, 0x01, 0x18, 0x54, 0x85, 0x00,
        0x02, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80};
    price_calc::utils::InputCodeStream code(bytecode);
    Price input(100, 0, 0, 0, 0, 0, 0);
    std::unordered_map<std::uint16_t, price_calc::interpreter::Value> globals;
    price_calc::interpreter::Run(input, kDefaultTripDetails, {}, code, globals);
    ASSERT_FALSE(std::get<bool>(globals.at(0)));
    ASSERT_FALSE(std::get<bool>(globals.at(1)));
    ASSERT_TRUE(std::get<bool>(globals.at(2)));
  }

  {
    Bytecode bytecode = Bytecode{0x19, 0x12, 0x34, 0x80};
    price_calc::utils::InputCodeStream code(bytecode);
    Price input(1, 1, 1, 1, 1, 1, 1);
    std::unordered_map<std::uint16_t, price_calc::interpreter::Value> globals{
        {0x1234, 1050.0}};
    auto result = std::get<0>(price_calc::interpreter::Run(
        input, kDefaultTripDetails, {}, code, globals));
    ASSERT_EQ(result.GetTotalPrice(), 1050);
  }
}
