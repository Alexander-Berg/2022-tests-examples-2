#include <userver/utest/utest.hpp>

#include <unordered_set>

#include <userver/formats/json/serialize.hpp>
#include <userver/fs/blocking/read.hpp>

#include <testing/source_path.hpp>

#include <clients/requirements/definitions.hpp>
#include <models/builders.hpp>

namespace taxi_requirements::models::descriptions {

namespace {

std::string ReadStatic(const std::string& name) {
  return fs::blocking::ReadFileContents(
      utils::CurrentSourcePath("tests/static/" + name));
}

}  // namespace

TEST(ModelsBuilders, BuildRequirementsMap) {
  const auto reqs_json = ReadStatic("requirements_handler_response.json");

  auto parsed_reqs =
      formats::json::FromString(reqs_json)
          .As<clients::requirements::ListAllRequirementsResponseBody>();

  const auto reqs_map = BuildRequirementsMap(std::move(parsed_reqs.data));

  EXPECT_EQ(reqs_map.size(), 8);

  std::unordered_set<std::string> requirement_names;
  for (const auto& [name, value] : reqs_map) {
    requirement_names.insert(name);
  }
  std::unordered_set<std::string> expected_requirements{
      "yellowcarnumber",
      "ski",
      "check",
      "childchair_moscow",
      "passengers_count",
      "childchair_for_child_tariff",
      "cargo_type",
      "childchair_v2",
  };
  EXPECT_EQ(requirement_names, expected_requirements);
}

}  // namespace taxi_requirements::models::descriptions
