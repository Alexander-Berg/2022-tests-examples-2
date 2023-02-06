#include "files_by_wildcard.hpp"
#include "file_guard.hpp"
#include "file_ops.hpp"

#include <boost/filesystem/operations.hpp>
#include <userver/fs/blocking/write.hpp>
#include <userver/logging/log.hpp>

#include <gtest/gtest.h>

// NOTE: `utils::CreateUniqueFile` creates files that start with a '.' (period)

TEST(FilesByWildcard, SingleFileNoWildcard) {
  namespace fs = boost::filesystem;
  const auto test_dir = fs::current_path() / "SingleFileNoWildcard";
  fs::create_directory(test_dir);
  utils::FileGuard test_dir_guard{test_dir};

  const auto test_file = utils::CreateUniqueFile(test_dir);
  utils::FileGuard guard{test_file};

  const auto result = utils::FilesByWildcard(test_file.native(), {});
  ASSERT_EQ(result.size(), 1u);
  EXPECT_EQ(result.front(), test_file);
}

TEST(FilesByWildcard, SingleFileWildcard) {
  namespace fs = boost::filesystem;
  const auto test_dir = fs::current_path() / "SingleFileWildcard";
  fs::create_directory(test_dir);
  utils::FileGuard test_dir_guard{test_dir};

  const auto test_file = utils::CreateUniqueFile(test_dir);
  utils::FileGuard guard{test_file};

  const auto result = utils::FilesByWildcard(test_file.string() + "*", {});
  ASSERT_EQ(result.size(), 1u);
  EXPECT_EQ(result.front(), test_file);
}

TEST(FilesByWildcard, ComplexWildcard) {
  namespace fs = boost::filesystem;

  const auto base_test_dir = fs::current_path() / "BaseFilesByWildcard";
  fs::create_directory(base_test_dir);
  utils::FileGuard base_test_dir_guard{base_test_dir};

  const auto test_dir = base_test_dir / "ComplexWildcard";
  fs::create_directory(test_dir);
  utils::FileGuard test_dir_guard{test_dir};

  const auto test_file = utils::CreateUniqueFile(test_dir);
  utils::FileGuard guard{test_file};

  const auto result = utils::FilesByWildcard(
      base_test_dir.native() + "/[Cc]omple[xX]Wi?dc?rd/.*", {});
  ASSERT_EQ(result.size(), 1u);
  EXPECT_EQ(result.front(), test_file);
}

TEST(FilesByWildcard, WildcardNoSubdirsVisitation) {
  namespace fs = boost::filesystem;
  const auto test_dir = fs::current_path() / "WildcardNoSubdirsVisitation";
  fs::create_directory(test_dir);
  utils::FileGuard test_dir_guard{test_dir};

  const auto nested_dir = test_dir / "NestedDirectory";
  fs::create_directory(nested_dir);
  utils::FileGuard nested_dir_guard{nested_dir};

  const auto test_file = utils::CreateUniqueFile(test_dir);
  utils::FileGuard guard{test_file};

  const auto nested_file = utils::CreateUniqueFile(nested_dir);
  utils::FileGuard nested_guard{nested_file};

  const auto result = utils::FilesByWildcard(test_dir.native() + "/.*", {});
  ASSERT_EQ(result.size(), 1u);
  EXPECT_EQ(result.front(), test_file);
}

TEST(FilesByWildcard, LogrotateLikeStructure) {
  namespace fs = boost::filesystem;
  const auto test_dir = fs::current_path() / "FileDirectoryWildcard";
  fs::create_directory(test_dir);
  utils::FileGuard test_dir_guard{test_dir};

  const auto dir_that_matches_base = test_dir / "dir_that_matches";
  fs::create_directory(dir_that_matches_base);
  utils::FileGuard dir_that_matches_base_guard{dir_that_matches_base};

  const auto dir_that_matches = dir_that_matches_base / "something";
  fs::create_directory(dir_that_matches);
  utils::FileGuard dir_that_matches_guard{dir_that_matches};

  ::fs::blocking::RewriteFileContents(
      (dir_that_matches / "service.log").string(), "");
  utils::FileGuard service_log_guard{dir_that_matches / "service.log"};

  ::fs::blocking::RewriteFileContents(
      (dir_that_matches / "service.log.1").string(), "");
  utils::FileGuard service_log_1_guard{dir_that_matches / "service.log.1"};

  ::fs::blocking::RewriteFileContents(
      (dir_that_matches / "service.log.1.gz").string(), "");
  utils::FileGuard log_1_gz_guard{dir_that_matches / "service.log.1.gz"};

  const auto dir_no_match = test_dir / "0_dir_no_match";
  fs::create_directory(dir_no_match);
  utils::FileGuard dir_no_match_guard{dir_no_match};

  utils::FileGuard no_match1_guard{utils::CreateUniqueFile(dir_no_match)};
  utils::FileGuard no_match2_guard{utils::CreateUniqueFile(dir_no_match)};
  utils::FileGuard no_match3_guard{utils::CreateUniqueFile(dir_no_match)};

  const std::string wildcard = (test_dir / "dir_that_matches/*/*.log").native();
  const auto result = utils::FilesByWildcard(wildcard, {});

  ASSERT_EQ(result.size(), 1u);
  EXPECT_EQ(result.front(), service_log_guard.Path());
}

TEST(FilesByWildcard, FileDirectoryWildcard) {
  namespace fs = boost::filesystem;
  const auto test_dir = fs::current_path() / "FileDirectoryWildcard";
  fs::create_directory(test_dir);
  utils::FileGuard test_dir_guard{test_dir};

  const auto dir_that_matches = test_dir / "dir_that_matches";
  fs::create_directory(dir_that_matches);
  utils::FileGuard dir_that_matches_guard{dir_that_matches};

  const auto test_file1 = utils::CreateUniqueFile(dir_that_matches);
  utils::FileGuard test_file1_guard{test_file1};
  const auto test_file2 = utils::CreateUniqueFile(dir_that_matches);
  utils::FileGuard test_file2_guard{test_file2};

  const auto dir_no_match = test_dir / "0_dir_no_match";
  fs::create_directory(dir_no_match);
  utils::FileGuard dir_no_match_guard{dir_no_match};

  utils::FileGuard no_match1_guard{utils::CreateUniqueFile(dir_no_match)};
  utils::FileGuard no_match2_guard{utils::CreateUniqueFile(dir_no_match)};
  utils::FileGuard no_match3_guard{utils::CreateUniqueFile(dir_no_match)};

  {
    const std::string wildcard = (test_dir / "*_matches/.*").native();
    const auto result = utils::FilesByWildcard(wildcard, {});

    ASSERT_EQ(result.size(), 2u);
    EXPECT_TRUE(result.front() == test_file1 || result.front() == test_file2);
    EXPECT_TRUE(result.back() == test_file1 || result.back() == test_file2);
    EXPECT_NE(result.front(), result.back());
  }

  {
    const std::string wildcard = (test_dir / "dir_that_*/.*").native();
    const auto result = utils::FilesByWildcard(wildcard, {});

    ASSERT_EQ(result.size(), 2u);
    EXPECT_TRUE(result.front() == test_file1 || result.front() == test_file2);
    EXPECT_TRUE(result.back() == test_file1 || result.back() == test_file2);
    EXPECT_NE(result.front(), result.back());
  }

  {
    const std::string wildcard = (test_dir / "dir_that_matches*/.*").native();
    const auto result = utils::FilesByWildcard(wildcard, {});

    ASSERT_EQ(result.size(), 2u);
    EXPECT_TRUE(result.front() == test_file1 || result.front() == test_file2);
    EXPECT_TRUE(result.back() == test_file1 || result.back() == test_file2);
    EXPECT_NE(result.front(), result.back());
  }

  {
    const std::string wildcard = (test_dir / "*_that_*/.*").native();
    const auto result = utils::FilesByWildcard(wildcard, {});

    ASSERT_EQ(result.size(), 2u);
    EXPECT_TRUE(result.front() == test_file1 || result.front() == test_file2);
    EXPECT_TRUE(result.back() == test_file1 || result.back() == test_file2);
    EXPECT_NE(result.front(), result.back());
  }

  {
    const std::string wildcard = (test_dir / "dir_that_matches").native();
    // `wildcard` is bad - it is not a file and does not contain `*`,`?` or '['
    const auto result = utils::FilesByWildcard(wildcard, {});
    ASSERT_TRUE(result.empty());
  }

  {
    const std::string wildcard = (test_dir / "dir_that_matches/*").native();
    const auto result = utils::FilesByWildcard(wildcard, {});
    ASSERT_TRUE(result.empty());  // `*` does not match points
  }

  {
    const std::string wildcard = (test_dir / "dir_that_matches/?*").native();
    const auto result = utils::FilesByWildcard(wildcard, {});
    ASSERT_TRUE(result.empty());  // `?` does not match points
  }

  {
    const std::string wildcard = (test_dir / "*/.*").native();
    const auto result = utils::FilesByWildcard(wildcard, {});
    ASSERT_EQ(result.size(), 5u);
  }

  {
    boost::system::error_code ec;
    fs::create_symlink(no_match1_guard.Path(), test_dir / "dir_symlink", ec);
    if (ec) {
      LOG_WARNING() << "Symlinks are not supported by this filesystem: " << ec;
      return;
    }
  }

  {
    utils::FileGuard symlink_dir_guard{test_dir / "dir_symlink"};
    const std::string wildcard = (test_dir / "dir_symlink/.*").native();
    EXPECT_ANY_THROW(utils::FilesByWildcard(wildcard, {}));
  }

  {
    auto symlink_file_path = dir_that_matches / ".symlink";
    fs::create_symlink(no_match1_guard.Path(), symlink_file_path);
    utils::FileGuard symlink_file_guard{symlink_file_path};

    const std::string wildcard = (test_dir / "dir_that_matches/.*").native();
    const auto result = utils::FilesByWildcard(wildcard, {});

    constexpr std::size_t results_expected = 3u;
    ASSERT_EQ(result.size(), results_expected);
    for (unsigned i = 0; i < results_expected; ++i) {
      EXPECT_TRUE(result[i] == test_file1 || result[i] == test_file2 ||
                  result[i] == symlink_file_path);
      EXPECT_NE(result[i], result[(i + 1) % results_expected]);
      EXPECT_NE(result[i], result[(i + 2) % results_expected]);
    }
  }
}

TEST(FilesByWildcard, ExcludeSingleFile) {
  namespace fs = boost::filesystem;
  const auto test_dir = fs::current_path() / "SingleFileNoWildcard";
  fs::create_directory(test_dir);
  utils::FileGuard test_dir_guard{test_dir};

  const auto test_file = utils::CreateUniqueFile(test_dir);
  utils::FileGuard guard{test_file};
  const auto pattern = test_file.native() + "*";

  {
    auto result = utils::FilesByWildcard(test_file.native(), {});
    ASSERT_EQ(result.size(), 1);
  }

  {
    auto result = utils::FilesByWildcard(pattern, {test_dir.native() + "/.*"});
    ASSERT_TRUE(result.empty());
  }

  {
    auto result =
        utils::FilesByWildcard(test_file.native(), {test_dir.native() + "/*"});
    ASSERT_EQ(result.size(), 1);
  }
}
