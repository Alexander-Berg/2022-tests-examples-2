#pragma once

#include <fstream>
#include <sstream>

#include <fmt/format.h>
#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>

#include <testing/source_path.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/utest/utest.hpp>

namespace js_pipeline {

const std::string kPathStatic{
    utils::CurrentSourcePath("tests/pipeline/static/")};

inline std::string Trim(const std::string& input) {
  std::string result;

  std::istringstream iss(input);

  for (std::string line; std::getline(iss, line);) {
    boost::trim_right(line);
    result += line + "\n";
  }

  boost::trim_right(result);

  return result;
}

inline std::string ReadResource(const std::string& filename) {
  const auto* test_info =
      ::testing::UnitTest::GetInstance()->current_test_info();
  const auto default_static_dir = kPathStatic + "default";
  const auto test_static_dir =
      kPathStatic +
      boost::filesystem::path(test_info->file()).filename().stem().string();
  std::array static_dirs{default_static_dir, test_static_dir};

  for (const auto& static_dir : static_dirs) {
    std::ifstream in(static_dir + "/" + filename);
    if (in) {
      return Trim(std::string((std::istreambuf_iterator<char>(in)),
                              std::istreambuf_iterator<char>()));
    }
  }

  throw std::runtime_error(fmt::format("Resource file open failure: {}/{}",
                                       fmt::join(static_dirs, ","), filename));
}

inline formats::json::Value ReadJsonResource(const std::string& filename) {
  return formats::json::FromString(ReadResource(filename));
}

}  // namespace js_pipeline
