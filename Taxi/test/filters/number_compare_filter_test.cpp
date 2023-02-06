#include <userver/utest/utest.hpp>

#include <string>
#include <vector>

#include <eventus/filters/number_compare_filter.hpp>

namespace {

using eventus::common::OperationArgs;
using OperationArgsV = std::vector<eventus::common::OperationArgument>;

template <typename T>
void MakeTest(T lhs_value, double rhs_value, std::string operator_name,
              bool expected, std::optional<double> precision = {}) {
  using namespace formats::json;

  OperationArgsV args{{"lhs_key", "value"},
                      {"rhs_value", rhs_value},
                      {"operator", operator_name}};

  if (precision.has_value()) {
    args.push_back({"precision", *precision});
  }

  std::string event_str = "{\"value\":" + std::to_string(lhs_value) + "}";

  auto filter = eventus::filters::NumberCompareFilter(OperationArgs(args));

  auto event = eventus::pipeline::Event(FromString(event_str));

  auto result = filter.Match(event);

  ASSERT_EQ(result.result == eventus::filters::FilterResult::kAccepted,
            expected);
}

}  // namespace

TEST(NumberCompareFilter, TestAllOperators) {
  MakeTest(10, 10, "equal_to", true);
  MakeTest(10.0, 10, "equal_to", true);
  MakeTest(11, 10, "equal_to", false);
  MakeTest(9, 10, "equal_to", false);

  MakeTest(10, 10, "not_equal_to", false);
  MakeTest(10.0, 10, "not_equal_to", false);
  MakeTest(11, 10, "not_equal_to", true);
  MakeTest(9, 10, "not_equal_to", true);

  MakeTest(10, 10, "greater", false);
  MakeTest(10.0, 10, "greater", false);
  MakeTest(11, 10, "greater", true);
  MakeTest(9, 10, "greater", false);

  MakeTest(10, 10, "less", false);
  MakeTest(10.0, 10, "less", false);
  MakeTest(11, 10, "less", false);
  MakeTest(9, 10, "less", true);

  MakeTest(10, 10, "greater_equal", true);
  MakeTest(10.0, 10, "greater_equal", true);
  MakeTest(11, 10, "greater_equal", true);
  MakeTest(9, 10, "greater_equal", false);

  MakeTest(10, 10, "less_equal", true);
  MakeTest(10.0, 10, "less_equal", true);
  MakeTest(11, 10, "less_equal", false);
  MakeTest(9, 10, "less_equal", true);
}

TEST(NumberCompareFilter, TestWithPrecision) {
  MakeTest(10.01, 10, "equal_to", true, 0.1);
  MakeTest(10, 10, "equal_to", true, 0.1);
  MakeTest(10.15, 10, "equal_to", false, 0.1);
  MakeTest(10.15, 10, "equal_to", true, 1);
  MakeTest(10.000009, 10, "equal_to", true);

  MakeTest(10.01, 10, "not_equal_to", false, 0.1);
  MakeTest(10, 10, "not_equal_to", false, 0.1);
  MakeTest(10.15, 10, "not_equal_to", true, 0.1);
  MakeTest(10.15, 10, "not_equal_to", false, 1);
  MakeTest(10.000009, 10, "not_equal_to", false);
}

TEST(NumberCompareFilter, IncorrectOperator) {
  OperationArgsV args{
      {"lhs_key", "value"}, {"rhs_value", 0.1}, {"operator", "incorrect"}};

  EXPECT_THROW(eventus::filters::NumberCompareFilter(OperationArgs(args)),
               std::exception);
}
