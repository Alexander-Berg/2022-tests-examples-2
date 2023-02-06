#include "file_ops.hpp"
#include "file_guard.hpp"

#include <boost/filesystem/operations.hpp>
#include <fstream>

#include <gtest/gtest.h>

TEST(FileOps, CreateAndDelete) {
  boost::filesystem::path path = utils::CreateUniqueFile();
  EXPECT_TRUE(boost::filesystem::exists(path));
  {
    utils::FileGuard guard{path};
    EXPECT_TRUE(boost::filesystem::exists(path));
  }
  EXPECT_FALSE(boost::filesystem::exists(path));
}

TEST(FileOps, CreateWriteDelete) {
  std::string path;
  {
    utils::FileGuard guard{utils::CreateUniqueFile()};
    path = guard.Path().string();
    { std::ofstream(path.c_str()) << "TEST"; }

    {
      std::string test_data;
      std::ifstream(path) >> test_data;
      EXPECT_EQ(test_data, "TEST");
    }
    EXPECT_TRUE(boost::filesystem::exists(path));
  }
  EXPECT_FALSE(boost::filesystem::exists(path));
}

TEST(FileOps, CreateRename) {
  boost::filesystem::path path = utils::CreateUniqueFile();
  EXPECT_TRUE(boost::filesystem::exists(path));

  utils::FileGuard to{utils::CreateUniqueFile()};
  boost::filesystem::rename(path, to.Path());
  EXPECT_FALSE(boost::filesystem::exists(path));
}

TEST(FileOps, CreateErase) {
  boost::filesystem::path path = utils::CreateUniqueFile();
  EXPECT_TRUE(boost::filesystem::exists(path));

  boost::filesystem::remove(path);
  EXPECT_FALSE(boost::filesystem::exists(path));

  EXPECT_ANY_THROW(boost::filesystem::rename(path, "./shall_not_be_created"));
  EXPECT_FALSE(boost::filesystem::exists("./shall_not_be_created"));
}
