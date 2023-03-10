#include <userver/utest/utest.hpp>

#include <boost/filesystem/operations.hpp>

#include <userver/dump/common.hpp>
#include <userver/dump/operations_encrypted.hpp>
#include <userver/fs/blocking/temp_directory.hpp>
#include <userver/tracing/span.hpp>

USERVER_NAMESPACE_BEGIN
using namespace dump;

namespace {
const SecretKey kTestKey{"12345678901234567890123456789012"};
}

UTEST(DumpEncFile, Smoke) {
  const auto dir = fs::blocking::TempDirectory::Create();
  const auto path = dir.GetPath() + "/file";

  auto scope_time = tracing::Span::CurrentSpan().CreateScopeTime("dump");
  EncryptedWriter w(path, kTestKey, boost::filesystem::perms::owner_read,
                    scope_time);

  w.Write(1);
  EXPECT_NO_THROW(w.Finish());

  auto size = boost::filesystem::file_size(path);
  EXPECT_EQ(size, 33);

  EncryptedReader r(path, kTestKey);
  EXPECT_EQ(r.Read<int32_t>(), 1);

  EXPECT_THROW(r.Read<int32_t>(), Error);

  EXPECT_NO_THROW(r.Finish());
}

UTEST(DumpEncFile, UnreadData) {
  const auto dir = fs::blocking::TempDirectory::Create();
  const auto path = dir.GetPath() + "/file";

  auto scope_time = tracing::Span::CurrentSpan().CreateScopeTime("dump");
  EncryptedWriter w(path, kTestKey, boost::filesystem::perms::owner_read,
                    scope_time);

  w.Write(1);
  EXPECT_NO_THROW(w.Finish());

  auto size = boost::filesystem::file_size(path);
  EXPECT_EQ(size, 33);

  EncryptedReader r(path, kTestKey);

  EXPECT_THROW(r.Finish(), Error);
}

UTEST(DumpEncFile, Long) {
  const auto dir = fs::blocking::TempDirectory::Create();
  const auto path = dir.GetPath() + "/file";

  auto scope_time = tracing::Span::CurrentSpan().CreateScopeTime("dump");
  EncryptedWriter w(path, kTestKey, boost::filesystem::perms::owner_read,
                    scope_time);

  for (int i = 0; i < 256; i++) w.Write(i);
  EXPECT_NO_THROW(w.Finish());

  auto size = boost::filesystem::file_size(path);
  EXPECT_EQ(size, 416);

  EncryptedReader r(path, kTestKey);
  for (int i = 0; i < 256; i++) EXPECT_EQ(r.Read<int32_t>(), i);

  EXPECT_THROW(r.Read<int32_t>(), Error);

  EXPECT_NO_THROW(r.Finish());
}

USERVER_NAMESPACE_END
