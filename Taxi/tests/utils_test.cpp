#include <fstream>

#include <gtest/gtest.h>

#include <experiments3_common/models/errors.hpp>
#include <experiments3_common/models/types.hpp>
#include <experiments3_common/utils/files.hpp>
#include <utils/experiments3/files.hpp>
#include <utils/hash.hpp>
#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>

#include <string>
#include <unordered_set>

namespace {

struct ContentSizeVisitor : public boost::static_visitor<size_t> {
  ContentSizeVisitor() {}

  size_t operator()(const std::unordered_set<std::string>& value) const {
    return value.size();
  }

  size_t operator()(const std::unordered_set<std::int64_t>& value) const {
    return value.size();
  }
};

}  // namespace

TEST(Exp3Utils, SplitString) {
  const auto value = std::string("abc\ndef\r\npqr");
  const auto lines = std::get<std::unordered_set<std::string>>(
      experiments3::utils::SplitIntoLines("string", value));

  ASSERT_EQ(lines.size(), static_cast<size_t>(3));
}

TEST(Exp3Utils, FileReading) {
  std::string filepath = SOURCE_DIR "/tests/static/utils/bad_file.string";
  auto file =
      experiments3::utils::ReadFileContentsByFileName(filepath, LogExtra());
  size_t size = file->Hashes().size();
  ASSERT_TRUE(size > 0);
}
