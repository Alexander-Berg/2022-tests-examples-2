#include <userver/utest/utest.hpp>

#include <userver/fs/blocking/read.hpp>
#include <userver/fs/blocking/temp_file.hpp>

#include <kuba-zip/writer.hpp>

#include "zip/zip.h"

namespace {
void CheckZipEntry(zip_t* zip, int index, const std::string& name,
                   const std::string& content) {
  EXPECT_EQ(zip_entry_openbyindex(zip, index), 0);

  EXPECT_EQ(zip_entry_name(zip), name);

  std::string buffer;
  void* entry_buf;
  size_t entry_buf_size;
  zip_entry_read(zip, &entry_buf, &entry_buf_size);
  buffer.assign((const char*)entry_buf, entry_buf_size);
  free(entry_buf);

  EXPECT_EQ(zip_entry_close(zip), 0);

  EXPECT_EQ(buffer, content);
}
}  // namespace

namespace kuba_zip {
TEST(Zip, ReadThatWritten) {
  std::string large_string(54321, 'z');
  large_string[112] = 'Z';
  large_string[935] = 'Z';

  auto temp_file = fs::blocking::TempFile::Create();
  {
    ZipWriter writer(temp_file.GetPath().c_str());
    writer.AddEntry("stored", "qwerty");
    writer.AddEntry("compressed", large_string);
    EXPECT_THROW(writer.AddEntry("", "!"), std::runtime_error);
  }

  // Check if compressed
  auto file_size = fs::blocking::ReadFileContents(temp_file.GetPath()).size();
  EXPECT_LT(file_size, large_string.size());
  EXPECT_LT(file_size, 1024);  // Just make sure we compress hard enought

  // Check contents
  auto zip =
      zip_open(temp_file.GetPath().c_str(), ZIP_DEFAULT_COMPRESSION_LEVEL, 'r');
  EXPECT_TRUE(zip);
  EXPECT_EQ(zip_entries_total(zip), 2);

  CheckZipEntry(zip, 0, "stored", "qwerty");
  CheckZipEntry(zip, 1, "compressed", large_string);
  zip_close(zip);
}
}  // namespace kuba_zip
