#include <gtest/gtest.h>

#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/filesystem.hpp>
#include <fstream>

#include <utils/datetime.hpp>
#include <utils/scope_guard.hpp>

#include <caches/dumper.hpp>
#include <utils/test_file_utils.hpp>

namespace caches {

TEST(CacheDumper, FileNameTest) {
  auto t = utils::datetime::Stringtime("2000-10-09T12:20:30+0000");
  details::DumpVersion version;
  version.protocol_version = 1;
  version.saved_at = t;

  auto filename = details::MakeFileName(version);
  EXPECT_EQ(filename, std::string("dump_2000-10-09T12:20:30+0000_version_1"));
  auto parsed = details::ParseFileName(filename);
  EXPECT_EQ(std::tie(parsed.protocol_version, parsed.saved_at),
            std::tie(version.protocol_version, version.saved_at));
}

TEST(CacheDumper, ClearTmpTest) {
  namespace bfs = boost::filesystem;
  const auto directory = utils::MakeRandomDumpDirectory();
  bfs::create_directories(directory);
  utils::ScopeGuard cleanup(
      [directory]() { utils::ClearDirectory(directory); });

  auto f1 = directory / "some_random_file";
  auto f2 = directory / "dump_2000-10-09T12:20:30+0000_version_1";
  auto f3 = directory / "dump_2000-10-09T12:20:30+0000_version_1.tmp";
  utils::CreateFile(f1);
  utils::CreateFile(f2);
  utils::CreateFile(f3);

  details::ClearTmp(directory.native(), LogExtra{});

  ASSERT_EQ(utils::ListDirectory(directory),
            (std::set<std::string>({f1.native(), f2.native()})));
}

TEST(CacheDumper, ClearDumps) {
  namespace bfs = boost::filesystem;
  const auto directory = utils::MakeRandomDumpDirectory();

  {
    bfs::create_directories(directory);
    utils::ScopeGuard cleanup(
        [directory]() { utils::ClearDirectory(directory); });

    auto f0 = directory / "some_random_file";
    auto f1 = directory / "dump_2000-10-09T12:20:30+0000_version_1.tmp";
    auto f2 = directory / "dump_2000-10-09T12:20:30+0000_version_1";
    auto f3 = directory / "dump_2000-10-09T12:20:30+0000_version_2";
    utils::CreateFile(f0);
    utils::CreateFile(f1);
    utils::CreateFile(f2);
    utils::CreateFile(f3);

    details::ClearDumps(directory.native(), 2, 1, LogExtra{});
    ASSERT_EQ(utils::ListDirectory(directory),
              (std::set<std::string>({f0.native(), f1.native(), f3.native()})));
  }

  {
    bfs::create_directories(directory);
    utils::ScopeGuard cleanup(
        [directory]() { utils::ClearDirectory(directory); });

    auto f0 = directory / "dump_2000-10-09T12:20:30+0000_version_1";
    auto f1 = directory / "dump_2000-12-09T12:20:30+0000_version_1";
    auto f2 = directory / "dump_2000-10-09T12:20:30+0000_version_2";
    auto f3 = directory / "dump_2000-11-09T12:20:30+0000_version_2";
    utils::CreateFile(f0);
    utils::CreateFile(f1);
    utils::CreateFile(f2);
    utils::CreateFile(f3);

    details::ClearDumps(directory.native(), 2, 1, LogExtra{});
    ASSERT_EQ(utils::ListDirectory(directory),
              (std::set<std::string>({f3.native()})));
  }

  {
    bfs::create_directories(directory);
    utils::ScopeGuard cleanup(
        [directory]() { utils::ClearDirectory(directory); });

    auto f0 = directory / "dump_2000-11-09T12:20:30+0000_version_0";
    auto f1 = directory / "dump_2000-10-09T12:20:30+0000_version_1";
    auto f2 = directory / "dump_2000-12-09T12:20:30+0000_version_1";
    auto f3 = directory / "dump_2000-10-09T12:20:30+0000_version_2";
    auto f4 = directory / "dump_2000-11-09T12:20:30+0000_version_2";
    auto f5 = directory / "dump_2000-11-09T12:20:30+0000_version_3";
    utils::CreateFile(f0);
    utils::CreateFile(f1);
    utils::CreateFile(f2);
    utils::CreateFile(f3);
    utils::CreateFile(f4);
    utils::CreateFile(f5);

    details::ClearDumps(directory.native(), 2, 2, LogExtra{});
    ASSERT_EQ(utils::ListDirectory(directory),
              (std::set<std::string>({f2.native(), f4.native()})));
  }
}

TEST(CacheDumper, FindLatest) {
  namespace bfs = boost::filesystem;
  const auto directory = utils::MakeRandomDumpDirectory();

  {
    bfs::create_directories(directory);
    utils::ScopeGuard cleanup(
        [directory]() { utils::ClearDirectory(directory); });

    auto f0 = directory / "some_random_file";
    auto f1 = directory / "dump_2000-10-09T12:20:30+0000_version_1.tmp";
    auto f2 = directory / "dump_2000-10-09T12:20:30+0000_version_1";
    auto f3 = directory / "dump_2000-11-09T12:20:30+0000_version_1";
    auto f4 = directory / "dump_2000-12-09T12:20:30+0000_version_2";
    utils::CreateFile(f0);
    utils::CreateFile(f1);
    utils::CreateFile(f2);
    utils::CreateFile(f3);
    utils::CreateFile(f4);

    auto latest = details::FindLatestDump(directory.native(), 1, LogExtra{});
    ASSERT_EQ(latest, std::optional<std::string>(f3.filename().native()));
  }

  {
    // no dump directory test
    auto latest = details::FindLatestDump(directory.native(), 1, LogExtra{});
    ASSERT_EQ(latest, std::optional<std::string>());
  }

  {
    // dump directory is a file
    utils::CreateFile(directory);
    utils::ScopeGuard cleanup(
        [directory]() { utils::ClearDirectory(directory); });
    ASSERT_THROW(details::FindLatestDump(directory.native(), 1, LogExtra{}),
                 DumperException);
  }

  {
    bfs::create_directories(directory);
    utils::ScopeGuard cleanup(
        [directory]() { utils::ClearDirectory(directory); });

    auto f0 = directory / "dump_2000-10-09T12:20:30+0000_version_1";
    utils::CreateFile(f0);

    auto latest = details::FindLatestDump(directory.native(), 2, LogExtra{});
    ASSERT_EQ(latest, std::optional<std::string>());
  }
}

TEST(CacheDumper, SaveAndLoad) {
  namespace bfs = boost::filesystem;
  const auto directory = utils::MakeRandomDumpDirectory();
  utils::ScopeGuard cleanup(
      [directory]() { utils::ClearDirectory(directory); });
  std::string file_name = "dump";

  auto writer = [](std::ostream& os) {
    {
      boost::archive::binary_oarchive arch1(os);
      int64_t b = 2000000000;
      arch1 << b;
    }
    {
      boost::archive::binary_oarchive arch2(os);
      int a = 5;
      arch2 << a;
    }
  };

  int64_t loaded_int64 = 0;
  int loaded_int = 0;
  auto reader = [&loaded_int, &loaded_int64](std::istream& is) {
    {
      boost::archive::binary_iarchive arch1(is);
      arch1 >> loaded_int64;
    }
    {
      boost::archive::binary_iarchive arch2(is);
      arch2 >> loaded_int;
    }
  };

  details::SaveToFileImpl(directory.native(), file_name, writer, LogExtra{});
  details::ReadFile((directory / file_name).native(), reader, LogExtra{});

  ASSERT_EQ(loaded_int64, 2000000000);
  ASSERT_EQ(loaded_int, 5);
}

}  // namespace caches
