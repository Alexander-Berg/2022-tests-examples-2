#include <gtest/gtest.h>

#include <fstream>
#include <functional>
#include <string>

#include <boost/filesystem.hpp>

#include <interpreter/interpreter.hpp>
#include <pricing-functions/helpers/convert_metadata.hpp>
#include <pricing-functions/lang/meta_modifications.hpp>
#include <pricing-functions/parser/ast_parser.hpp>
#include <pricing-functions/parser/parser.hpp>
#include <testing/source_path.hpp>
#include <tests/test_utils.hpp>
#include <userver/crypto/base64.hpp>
#include <userver/engine/run_standalone.hpp>
#include <userver/utest/utest.hpp>

namespace {

using price_calc::interpreter::Bytecode;
using price_calc::interpreter::Info;
using price_calc::interpreter::Infos;
using price_calc::interpreter::TripDetails;
using price_calc::models::Price;

struct SharedTestData {
  std::optional<lang::models::Program> ast;
};

struct TestSuitInfo {
  std::string name;
  std::string title;
  std::shared_ptr<test_utils::TestData> data;
  size_t case_id;
  std::optional<size_t> ride_id;
  std::shared_ptr<SharedTestData> shared_data;
};

std::vector<TestSuitInfo> ListCases() {
  using boost::filesystem::directory_iterator;
  std::vector<TestSuitInfo> result;
  const std::string base_path(utils::CurrentSourcePath("src/tests/test_data/"));
  for (directory_iterator itr(base_path); itr != directory_iterator(); ++itr) {
    const auto name = itr->path().filename().generic_string();

    const auto data = std::make_shared<test_utils::TestData>(base_path + name);

    const auto shared_data = std::make_shared<SharedTestData>();

    for (size_t i = 0; i < data->GetTestcases().size(); ++i) {
      result.push_back(TestSuitInfo{name, name + "_case_" + std::to_string(i),
                                    data, i, std::nullopt, shared_data});
      for (size_t j = 0; j < data->GetTestcases().at(i).fix_cases.size(); ++j) {
        result.push_back(TestSuitInfo{
            name,
            name + "_case_" + std::to_string(i) + "_ride_" + std::to_string(j),
            data, i, j, shared_data});
      }
    }
  }

  std::sort(result.begin(), result.end(), [](const auto& a, const auto& b) {
    if (a.name != b.name) {
      return a.name < b.name;
    } else if (a.case_id != b.case_id) {
      return a.case_id < b.case_id;
    } else {
      if (a.ride_id && b.ride_id) {
        return *a.ride_id < *b.ride_id;
      } else {
        return !!b.ride_id;
      }
    }
  });
  return result;
}

void ExpectEqual(const Price& actual, const Price& expected) {
  static constexpr double kEpsilon = 1e-12;

  EXPECT_NEAR(actual.boarding, expected.boarding, kEpsilon);
  EXPECT_NEAR(actual.distance, expected.distance, kEpsilon);
  EXPECT_NEAR(actual.time, expected.time, kEpsilon);
  EXPECT_NEAR(actual.waiting, expected.waiting, kEpsilon);
  EXPECT_NEAR(actual.requirements, expected.requirements, kEpsilon);
  EXPECT_NEAR(actual.transit_waiting, expected.transit_waiting, kEpsilon);
  EXPECT_NEAR(actual.destination_waiting, expected.destination_waiting,
              kEpsilon);
}

Bytecode BytesToVector(const std::string& bytes) {
  std::string str = crypto::base64::Base64Decode(bytes);
  return std::vector<uint8_t>(std::make_move_iterator(str.begin()),
                              std::make_move_iterator(str.end()));
}

}  // namespace

class ParserCompiler : public ::testing::TestWithParam<TestSuitInfo> {};

TEST_P(ParserCompiler, Parse) {
  using RemoveUnusedVariablesMode = ::handlers::libraries::pricing_functions::
      PricingCompilationOptionsRemoveunusedvariables;
  engine::TaskProcessorPoolsConfig config{};
  config.coro_stack_size = 256 * 1024 + 123;
  const auto& [name, title, data_ptr, case_id, ride_id, shared_data] =
      GetParam();
  const auto& data = *data_ptr;
  engine::RunStandalone(
      1, config,
      [data = data, shared_data = shared_data, case_id = case_id,
       ride_id = ride_id]() {
        if (!shared_data->ast) {
          if (data.GetCompilationError() != test_utils::kNoCheck) {
            try {
              shared_data->ast = parser::Parse(data.GetCode(), data.GetExtra());
              FAIL();
            } catch (const std::exception& e) {
              EXPECT_EQ(e.what(), data.GetCompilationError());
              return;
            }
          } else {
            shared_data->ast = parser::Parse(data.GetCode(), data.GetExtra());
          }
        }

        const auto& ast = *shared_data->ast;

        if (data.GetAst() != test_utils::kNoCheck) {
          EXPECT_EQ(ast.Serialize(), data.GetAst());
        } else {
          std::cerr << "Code parser test skipped" << std::endl;
        }

        const auto& test_case = data.GetTestcases().at(case_id);
        const auto& vars = test_case.fix;

        if (ride_id) {
          const auto& features =
              lang::models::ListFeatures(test_case.price_calc_version);

          lang::models::GlobalLinkContext link_context{};
          lang::models::GlobalCompilationContext compilation_context{};
          const auto& simplified_ast =
              ast.Link(vars, std::nullopt, features, link_context);
          const auto& compiled = test_utils::ToHex(simplified_ast.Compile(
              test_case.taximeter_metadata,
              {true /* drop_empty_return */,
               RemoveUnusedVariablesMode::kEnableWithChecks},
              compilation_context));

          const auto& fix_case = test_case.fix_cases.at(*ride_id);

          auto trip = std::make_optional(fix_case.trip);
          lang::models::GlobalLinkContext link_context_fix{};
          const auto& simplified_ast_fix =
              ast.Link(vars, trip, features, link_context_fix);

          if (fix_case.simplified_ast != test_utils::kNoCheck)
            EXPECT_EQ(simplified_ast_fix.Serialize(),
                      fix_case.simplified_ast);  // test simplifier

          std::unordered_map<std::string, uint16_t> map_taximeter_metadata;
          for (const auto& item : fix_case.taximeter_metadata) {
            map_taximeter_metadata[item.key] = item.value;
          }
          const auto& compiled_fix =
              test_utils::ToHex(simplified_ast_fix.Compile(
                  helpers::ConvertMetadata(map_taximeter_metadata),
                  {true /* drop_empty_return */,
                   RemoveUnusedVariablesMode::kEnableWithChecks},
                  compilation_context));
          if (fix_case.compiled != test_utils::kNoCheck)
            EXPECT_EQ(compiled_fix, fix_case.compiled);  // test compiler

          for (const auto& ride : fix_case.ride_cases) {
            const auto& initial_price = ride.initial_price;
            const auto& price = ride.price;
            const auto& fixed_price = ride.fixed_price;
            const auto& trip_details = ride.taximeter_trip;

            std::unordered_map<std::string, int32_t> metadata_mapping;
            for (const auto& each : test_case.taximeter_metadata) {
              metadata_mapping.emplace(each.key, each.value);
            }

            auto output = price_calc::interpreter::RunBulk(
                initial_price, trip_details,
                BytesToVector(crypto::base64::Base64Encode(
                    test_utils::FromHex(compiled))),
                1.0, metadata_mapping);
            ExpectEqual(std::get<1>(output), price);  // test interpreter

            auto output_fix = price_calc::interpreter::RunBulk(
                initial_price, trip_details,
                BytesToVector(crypto::base64::Base64Encode(
                    test_utils::FromHex(compiled_fix))),
                1.0, metadata_mapping);
            ExpectEqual(std::get<1>(output_fix),
                        fixed_price);  // test interpreter

            const auto& features_ =
                lang::models::ListFeatures(ride.price_calc_version);

            try {
              if (trip_details.waiting_time_.count() == 0 &&
                  trip_details.waiting_in_transit_time_.count() == 0 &&
                  trip_details.waiting_in_destination_time_.count() == 0 &&
                  trip_details.user_options_.empty() &&
                  trip_details.user_meta_.empty()) {
                auto ast_fix =
                    ast.CalculateFix(vars, *trip, {{}, initial_price},
                                     features_, {}, true /* enable_debug */);

                ExpectEqual(ast_fix.price,
                            fixed_price);  // test ast interpreter

                if (fix_case.expected_lines_visited) {
                  const auto& expected_lines_visited =
                      *fix_case.expected_lines_visited;
                  if (ast_fix.debug_info) {
                    std::vector<size_t> debug_line{
                        ast_fix.debug_info->visited_lines.begin(),
                        ast_fix.debug_info->visited_lines.end()};
                    std::sort(debug_line.begin(), debug_line.end());
                    ASSERT_EQ(expected_lines_visited,
                              ast_fix.debug_info->visited_lines);
                  }
                }

                if (ride.metadata) {
                  const auto& fix_metadata = ast_fix.metadata;

                  EXPECT_EQ(ride.metadata->size(), fix_metadata.size());

                  for (const auto& [key, value] : *ride.metadata) {
                    EXPECT_EQ(fix_metadata.count(key), 1);
                    EXPECT_DOUBLE_EQ(fix_metadata.at(key), value);
                  }
                }
              } else {
                auto ast_fix = ast.CalculateFix(
                    vars, *trip,
                    {{static_cast<double>(trip_details.waiting_time_.count()),
                      static_cast<double>(
                          trip_details.waiting_in_transit_time_.count()),
                      static_cast<double>(
                          trip_details.waiting_in_destination_time_.count()),
                      trip_details.user_options_, trip_details.user_meta_},
                     initial_price},
                    features, {});

                ExpectEqual(ast_fix.price,
                            price);  // test ast interpreter
                if (ride.metadata) {
                  const auto& fix_metadata = ast_fix.metadata;

                  EXPECT_EQ(ride.metadata->size(), fix_metadata.size());

                  for (const auto& [key, value] : *ride.metadata) {
                    EXPECT_EQ(fix_metadata.count(key), 1);
                    EXPECT_DOUBLE_EQ(fix_metadata.at(key), value);
                  }
                }
              }
            } catch (const parser::AssertionError&) {
              // FIXME: this check cause stack overflow in test
              // ASSERT_EQ(data.GetAssertionError(), er.what());
            }
          }
        } else {
          lang::models::GlobalLinkContext link_context{};
          const auto& simplified_ast =
              ast.Link(vars, std::nullopt,
                       lang::models::ListFeatures(test_case.price_calc_version),
                       link_context);
          auto sast = simplified_ast.Serialize();
          if (test_case.simplified_ast != test_utils::kNoCheck)
            EXPECT_EQ(simplified_ast.Serialize(),
                      test_case.simplified_ast);  // test simplifier

          lang::models::GlobalCompilationContext compilation_context{};
          const auto& compiled = test_utils::ToHex(simplified_ast.Compile(
              test_case.taximeter_metadata,
              {true /* drop_empty_return */,
               RemoveUnusedVariablesMode::kEnableWithChecks},
              compilation_context));
          if (test_case.compiled != test_utils::kNoCheck)
            EXPECT_EQ(compiled, test_case.compiled);  // test compiler
        }
      });
}

INSTANTIATE_TEST_SUITE_P(ParserCompiler, ParserCompiler,
                         ::testing::ValuesIn(ListCases()),
                         ([](const auto& param) { return param.param.title; }));
