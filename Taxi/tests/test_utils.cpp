#include "test_utils.hpp"

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/serialize_container.hpp>
#include <userver/formats/json/serialize_duration.hpp>

#include <pricing-functions/helpers/adapted_io.hpp>
#include <pricing-functions/helpers/bv_optional_parse.hpp>
#include <pricing-functions/helpers/price_calc_io.hpp>

#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>
#include <fstream>
#include <iomanip>
#include <set>
#include <sstream>

namespace {
const std::string kBackendVariables = "backend_variables";
const std::string kTripDetails = "trip_details";
const std::string kOutputPrice = "output_price";
const std::string kTaximeterTripDetails = "taximeter_trip_details";
const std::string kFixCases = "fix_cases";
const std::string kRides = "rides";
const std::string kSimplified = "simplified";
const std::string kSimplifiedFix = "simplified_fix";
const std::string kCompiled = "compiled";
const std::string kTaximeterMetadata = "taximeter_metadata";
const std::string kCompiledFix = "compiled_fix";
const std::string kInitialPrice = "initial_price";
const std::string kSimplifiedDot = "simplified_dot";
const std::string kFixedPrice = "fixed_price";
const std::string kMetadata = "metadata";
const std::string kPriceCalcVersion = "price_calc_version";
const std::string kExpectedLinesVisited = "expected_lines_visited";

const price_calc::models::Price kNormalPrice(1, 1, 1, 1, 1, 1, 1);

}  // namespace

namespace test_utils {

std::string Trim(std::string str) {
  if (str.empty()) {
    return str;
  }
  while (std::isspace(str.back())) {
    str.pop_back();
  }
  return str;
}

std::string ToHex(const price_calc::models::BinaryData& binary) {
  std::ostringstream os;

  bool first = true;

  for (const unsigned char b : binary) {
    os << (first ? "" : " ") << std::hex << std::setfill('0') << std::setw(2)
       << static_cast<unsigned>(b);
    first = false;
  }

  return os.str();
}

std::string FromHex(const std::string& hex) {
  std::istringstream is(hex);
  std::string result;

  while (is.good()) {
    std::string byte;
    is >> byte;
    if (byte.empty()) {
      continue;
    }

    result.push_back(std::stoi(byte, nullptr, 16));
  }
  return result;
}

TestData::TestCase::FixCase::RideCase ParseRide(
    const formats::json::Value& json, const std::string& filename,
    int test_case_number, bool& has_trip_details,
    std::string price_calc_version) {
  const auto& taximeter_trip =
      json[kTaximeterTripDetails].As<price_calc::interpreter::TripDetails>(
          price_calc::interpreter::TripDetails(
              0, std::chrono::seconds(0l), std::chrono::seconds(0l),
              std::chrono::seconds(0l), std::chrono::seconds(0l), {}, {}));
  has_trip_details = json.HasMember(kTaximeterTripDetails);
  const auto& initial_price =
      json[kInitialPrice].IsDouble()
          ? kNormalPrice.Split(json[kInitialPrice].As<double>())
          : json[kInitialPrice].As<price_calc::models::Price>(kNormalPrice);

  if (!json.HasMember(kOutputPrice) && !json.HasMember(kFixedPrice))
    throw std::invalid_argument("No any price found in " + filename +
                                " testcase #" +
                                std::to_string(test_case_number));
  std::optional<price_calc::models::Price> price;
  if (json.HasMember(kOutputPrice))
    price = json[kOutputPrice].IsDouble()
                ? kNormalPrice.Split(json[kOutputPrice].As<double>())
                : json[kOutputPrice].As<price_calc::models::Price>();

  std::optional<price_calc::models::Price> fixed_price;
  if (json.HasMember(kFixedPrice))
    fixed_price = json[kOutputPrice].IsDouble()
                      ? kNormalPrice.Split(json[kFixedPrice].As<double>())
                      : json[kFixedPrice].As<price_calc::models::Price>();

  std::optional<std::unordered_map<std::string, double>> metadata;
  if (json.HasMember(kMetadata)) {
    metadata = json[kMetadata].As<std::unordered_map<std::string, double>>();
  }

  if (json.HasMember(kPriceCalcVersion)) {
    price_calc_version = json[kPriceCalcVersion].As<std::string>();
  }

  return TestData::TestCase::FixCase::RideCase{
      initial_price,
      taximeter_trip,
      price ? *price : *fixed_price,
      fixed_price ? *fixed_price : *price,
      metadata,
      price_calc_version};
}

TestData::TestCase::FixCase ParseFix(const formats::json::Value& json,
                                     const std::string& simplified,
                                     const std::string& compiled,
                                     const std::string& filename,
                                     int test_case_number,
                                     const std::string& price_calc_version) {
  TestData::TestCase::FixCase fix_case;
  if (json.HasMember(kSimplifiedFix))
    fix_case.simplified_ast = json[kSimplifiedFix].As<std::string>();
  else
    fix_case.simplified_ast = simplified;

  if (json.HasMember(kCompiledFix))
    fix_case.compiled = json[kCompiledFix].As<std::string>();
  else
    fix_case.compiled = compiled;

  if (json.HasMember(kTaximeterMetadata)) {
    auto taximeter_metadata = formats::parse::Parse(
        json[kTaximeterMetadata],
        formats::parse::To<std::unordered_map<std::string, uint16_t>>());
    for (const auto& i : taximeter_metadata) {
      fix_case.taximeter_metadata.insert({{i.first}, i.second});
    }
  }

  bool has_taximeter_trip_details = false;

  if (json.HasMember(kRides)) {
    fix_case.ride_cases.reserve(json[kRides].GetSize());
    for (const auto& ride : json[kRides])
      fix_case.ride_cases.push_back(ParseRide(ride, filename, test_case_number,
                                              has_taximeter_trip_details,
                                              price_calc_version));
  } else {
    fix_case.ride_cases.push_back(ParseRide(json, filename, test_case_number,
                                            has_taximeter_trip_details,
                                            price_calc_version));
  }

  if (json.HasMember(kTripDetails)) {
    fix_case.trip = json[kTripDetails].As<lang::variables::TripDetails>();
    if (!has_taximeter_trip_details) {
      for (auto& ride : fix_case.ride_cases) {
        ride.taximeter_trip.total_time_ =
            std::chrono::seconds(static_cast<long>(fix_case.trip.time));
        ride.taximeter_trip.total_distance_ = fix_case.trip.distance;
        ride.taximeter_trip.waiting_time_ = std::chrono::seconds(0l);
        ride.taximeter_trip.waiting_in_transit_time_ = std::chrono::seconds(0l);
        ride.taximeter_trip.waiting_in_destination_time_ =
            std::chrono::seconds(0l);
      }
    }
  } else {
    if (fix_case.ride_cases.size() == 1)
      fix_case.trip = lang::variables::TripDetails{
          fix_case.ride_cases.back().taximeter_trip.total_distance_,
          static_cast<double>(
              fix_case.ride_cases.back().taximeter_trip.total_time_.count())};
    else
      fix_case.trip = lang::variables::TripDetails{0, 0};
  }

  fix_case.expected_lines_visited =
      json[kExpectedLinesVisited]
          .As<std::optional<std::unordered_set<size_t>>>();

  return fix_case;
}

std::string ReadFile(const std::string& file) {
  std::ifstream f(file);
  return std::string((std::istreambuf_iterator<char>(f)),
                     std::istreambuf_iterator<char>());
}

TestData::TestData(const std::string& filename_prefix)
    : code_(Trim(ReadFile(filename_prefix + "/code"))),
      ast_(boost::trim_copy(ReadFile(filename_prefix + "/ast"))),
      compilation_error_(
          boost::trim_copy(ReadFile(filename_prefix + "/compilation_error"))),
      expected_assertion_error_(
          boost::trim_copy(ReadFile(filename_prefix + "/assertion_error"))) {
  ParseTestcases(filename_prefix);
  if (!test_cases_.empty()) {
    if (test_cases_.front().simplified_dot == kNoCheck) {
      const auto& simplified_dot =
          ReadFile(filename_prefix + "/simplified.dot");
      if (!simplified_dot.empty())
        test_cases_.front().simplified_dot = simplified_dot;
    }
  }
  if (code_.empty())
    throw std::invalid_argument("Now code in " + filename_prefix);
  if (ast_.empty()) {
    ast_ = kNoCheck;
  }

  if (compilation_error_.empty()) {
    compilation_error_ = kNoCheck;
  }

  if (expected_assertion_error_.empty()) {
    expected_assertion_error_ = kNoCheck;
  }

  const auto& extra = ReadFile(filename_prefix + "/extra.json");
  if (!extra.empty()) {
    extra_ = formats::json::FromString(extra).As<std::vector<std::string>>();
  }
}

std::string ReadOtherFile(const std::string& filename_prefix,
                          std::string file_link) {
  if (file_link.empty()) return kNoCheck;
  if (file_link.front() != '#')
    throw std::invalid_argument(
        "Simplified dot must be link to file but got: " + file_link);
  file_link[0] = '/';
  return ReadFile(filename_prefix + file_link);
}

void TestData::ParseTestcases(const std::string& filename_prefix) {
  static const price_calc::models::Price kUnaryPriceValue(1, 1, 1, 1, 1, 1, 1);
  const auto& filename = filename_prefix + "/test_cases.json";
  try {
    const auto& all_cases = formats::json::blocking::FromFile(filename);

    test_cases_.reserve(all_cases.GetSize());
    for (const auto& testcase : all_cases) {
      if (!testcase.HasMember(kBackendVariables))
        throw std::invalid_argument("No " + kBackendVariables + " found in " +
                                    filename + " testcase #" +
                                    std::to_string(test_cases_.size()));

      TestCase test_case;
      test_case.simplified_ast =
          testcase[kSimplified].As<std::string>(kNoCheck);
      if (!test_case.simplified_ast.empty())
        if (test_case.simplified_ast.front() == '#')
          test_case.simplified_ast =
              Trim(ReadOtherFile(filename_prefix, test_case.simplified_ast));
      test_case.compiled = testcase[kCompiled].As<std::string>(kNoCheck);

      if (testcase.HasMember(kPriceCalcVersion)) {
        test_case.price_calc_version =
            testcase[kPriceCalcVersion].As<std::string>();
      } else {
        test_case.price_calc_version = "latest";
      }

      if (testcase.HasMember(kTaximeterMetadata)) {
        auto taximeter_metadata = formats::parse::Parse(
            testcase[kTaximeterMetadata],
            formats::parse::To<std::unordered_map<std::string, uint16_t>>());
        for (const auto& i : taximeter_metadata) {
          test_case.taximeter_metadata.insert({{i.first}, i.second});
        }
      }

      if (!test_case.compiled.empty())
        if (test_case.compiled.front() == '#')
          test_case.compiled =
              Trim(ReadOtherFile(filename_prefix, test_case.compiled));

      if (testcase.HasMember(kSimplifiedDot))
        test_case.simplified_dot = ReadOtherFile(
            filename_prefix, testcase[kSimplifiedDot].As<std::string>());
      else
        test_case.simplified_dot = kNoCheck;

      if (!testcase.HasMember(kFixCases)) {
        test_case.fix_cases.push_back(ParseFix(
            testcase, test_case.simplified_ast, test_case.compiled, filename,
            test_cases_.size(), test_case.price_calc_version));
      } else {
        test_case.fix_cases.reserve(testcase[kFixCases].GetSize());
        for (const auto& fix : testcase[kFixCases]) {
          test_case.fix_cases.push_back(ParseFix(
              fix, test_case.simplified_ast, test_case.compiled, filename,
              test_cases_.size(), test_case.price_calc_version));
        }
      }

      test_case.fix = formats::parse::ParseBackendVariablesOptional(
          testcase[kBackendVariables]);
      test_cases_.emplace_back(std::move(test_case));
    }
  } catch (const std::exception& er) {
    throw std::invalid_argument("Cannot read file " + filename + ": " +
                                er.what());
  }
}

}  // namespace test_utils
