#include <gtest/gtest.h>

#include <fstream>
#include <streambuf>

#include <config/config.hpp>
#include <mongo/mongo.hpp>
#include <utils/helpers/json.hpp>

using namespace config;

class ConfigTest : public ::testing::TestWithParam<const char*> {};

TEST_P(ConfigTest, ParseJson) {
  const std::string path{CONFIG_FALLBACK_DIR "/configs.json"};
  std::ifstream ifs(path);
  std::string content((std::istreambuf_iterator<char>(ifs)),
                      (std::istreambuf_iterator<char>()));
  ASSERT_NO_THROW(utils::helpers::ParseJson(content));
}
