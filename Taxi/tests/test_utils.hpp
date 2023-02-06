#pragma once

#include <interpreter/interpreter.hpp>
#include <models/binary_data.hpp>
#include <models/composite_price.hpp>
#include <pricing-functions/lang/meta_modifications.hpp>
#include <pricing-functions/lang/variables.hpp>

namespace test_utils {

const std::string kNoCheck = "none";

std::string ToHex(const price_calc::models::BinaryData& binary);
std::string FromHex(const std::string& hex);

struct TestData {
 public:
  TestData(const std::string& filename_prefix);

  const std::string& GetCode() const { return code_; }
  const std::vector<std::string>& GetExtra() const { return extra_; }
  const std::string& GetAst() const { return ast_; }
  const std::string& GetCompilationError() const { return compilation_error_; }
  const std::string& GetAssertionError() const {
    return expected_assertion_error_;
  }

  struct TestCase {
    lang::variables::BackendVariables fix;
    std::string simplified_ast;
    std::string simplified_dot;
    std::string compiled;
    std::unordered_set<lang::meta_modifications::MetaId> taximeter_metadata;
    std::string price_calc_version;

    struct FixCase {
      lang::variables::TripDetails trip;
      std::string simplified_ast;
      std::string compiled;
      std::unordered_set<lang::meta_modifications::MetaId> taximeter_metadata;
      std::optional<std::unordered_set<size_t>> expected_lines_visited;

      struct RideCase {
        price_calc::models::Price initial_price;
        price_calc::interpreter::TripDetails taximeter_trip;
        price_calc::models::Price price;
        price_calc::models::Price fixed_price;
        std::optional<std::unordered_map<std::string, double>> metadata;
        std::string price_calc_version;
      };
      std::vector<RideCase> ride_cases;
    };
    std::vector<FixCase> fix_cases;
  };
  using TestCases = std::vector<TestCase>;
  const TestCases& GetTestcases() const { return test_cases_; }

 private:
  void ParseTestcases(const std::string& filename_prefix);
  std::string code_;
  std::vector<std::string> extra_;
  std::string ast_;
  std::string compilation_error_;
  std::string expected_assertion_error_;

  TestCases test_cases_;
};

}  // namespace test_utils
