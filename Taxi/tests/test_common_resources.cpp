#include <gtest/gtest.h>

#include <boost/algorithm/string.hpp>

#include <ml/common/filesystem.hpp>
#include <ml/common/json.hpp>
#include <ml/common/resources.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("common_resources");

class DummyResource {
 public:
  DummyResource(const boost::filesystem::path& path,
                [[maybe_unused]] bool mock_mode) {
    data = ml::common::FromJsonString<
        std::unordered_map<std::string, std::string>>(
        ml::common::ReadFileContents((path / "config.json").string()));
  }

  std::unordered_map<std::string, std::string> data;
};

std::vector<std::string> Split(const std::string& str, const std::string& sep) {
  std::vector<std::string> result;
  boost::algorithm::split(result, str, boost::algorithm::is_any_of(sep),
                          boost::token_compress_on);
  return result;
}

}  // namespace

TEST(CommonResources, loaders) {
  const auto resources_path = kTestDataDir + "/resources_dir";

  ml::common::MapResourceWrapper<DummyResource> map_resource(resources_path,
                                                             true);
  const auto resource = map_resource.Get("first_resource_dir");
  ASSERT_EQ(resource->data.at("first_key"), "first_value");

  ASSERT_TRUE(map_resource.Contains("second_resource_dir"));
  ASSERT_FALSE(map_resource.Contains("second_dir_resource"));
  ASSERT_FALSE(map_resource.Contains(""));

  for (auto [name, res] : map_resource) {
    ASSERT_FALSE(name.empty());
    const auto str_number = Split(name, "_")[0];
    ASSERT_EQ(str_number, Split(res->data.at(str_number + "_key"), "_")[0]);
  }
}
