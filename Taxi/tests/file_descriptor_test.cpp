#include "file_descriptor.hpp"
#include "file_guard.hpp"
#include "file_ops.hpp"

#include <userver/fs/blocking/temp_file.hpp>

#include <boost/filesystem/operations.hpp>

#include <gtest/gtest.h>

TEST(FileDescriptor, Operations) {
  auto temp_file = fs::blocking::TempFile::Create();
  EXPECT_TRUE(boost::filesystem::exists(temp_file.GetPath()));

  EXPECT_NO_THROW(utils::FileDescriptor::Open(
      temp_file.GetPath(), utils::FileDescriptor::OpenFlag::kRead));
  EXPECT_THROW(
      utils::FileDescriptor::OpenExistingDirectory(temp_file.GetPath()),
      std::system_error);
}

TEST(FileDescriptor, FileIdAfterRemove) {
  auto temp_file = fs::blocking::TempFile::Create();
  auto fd = utils::FileDescriptor::Open(temp_file.GetPath(),
                                        utils::FileDescriptor::OpenFlag::kRead);

  const auto id = fd.GetId();
  boost::filesystem::remove(fd.Path());
  EXPECT_EQ(fd.GetId(), id) << "FileId changed for a removed file";

  const boost::filesystem::path replacement = utils::CreateUniqueFile();
  boost::filesystem::rename(replacement, fd.Path());
}
