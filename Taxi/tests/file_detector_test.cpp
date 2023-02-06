#include "file_detector.hpp"

#include <elastic/servers.hpp>
#include "file_guard.hpp"
#include "file_ops.hpp"
#include "token_vendor.hpp"

#include <boost/filesystem/operations.hpp>
#include <fstream>

#include <testing/taxi_config.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/fs/blocking/temp_file.hpp>
#include <userver/logging/log.hpp>
#include <userver/tracing/tracer.hpp>
#include <userver/utest/http_client.hpp>
#include <userver/utest/utest.hpp>

#include "open_files_count.hpp"

using namespace pilorama;

namespace {

struct FakeServers final
    : public ::boost::base_from_member<TokenVendor>,  // workaround
      public elastic::Servers {
 public:
  FakeServers(const OutputConfig& output, clients::http::Client& http,
              Statistics& statistics)
      : base_from_member(output.hosts.size(), utils::BytesPerSecond{0}),
        elastic::Servers(output, http, statistics, base_from_member::member) {}
  ~FakeServers() = default;

 private:
  OnResponseAction OnResponse(HttpResponse /*response*/,
                              HttpRequest /*request*/) override {
    return OnResponseAction::OK;
  }
};

struct FileDetectorTest {
  const utils::FileGuard sync_db_file{utils::CreateUniqueFile()};
  pilorama::syncdb::SyncDb db{sync_db_file.Path()};

  const utils::FileGuard directory_file{boost::filesystem::current_path() /
                                        "FileDetectorTest"};
  ConfigEntry conf = {
      {},
      {},
      OutputConfig{
          "", "index", "error_index", {"localhost:1234", "localhost:4321"}}};

  const std::shared_ptr<clients::http::Client> http_client_ptr =
      utest::CreateHttpClient();
  pilorama::Statistics stats{1};
  FakeServers http{conf.output, *http_client_ptr, stats};

  const size_t open_files_on_start =
      testing::OpenFilesCountWithPrefix(directory_file.Path());

  FileDetectorTest() {
    boost::system::error_code ignore;
    boost::filesystem::remove_all(directory_file.Path(), ignore);

    boost::filesystem::create_directory(directory_file.Path());
    conf.input.paths.push_back(directory_file.Path().string() + "/.*");
    conf.input.ignore_older = std::chrono::seconds{10};
  }

  void ExpectFileDiff(int diff, int line) const {
    EXPECT_EQ(static_cast<size_t>(open_files_on_start + diff),
              testing::OpenFilesCountWithPrefix(directory_file.Path()))
        << "At line " << line;
  }

  auto GetFileRotationsStat() const { return stats.file_rotations.Load(); }

  utils::FileGuard Make1ByteFileAndGuard() {
    auto path = utils::CreateUniqueFile(directory_file.Path());
    std::ofstream{path.c_str()} << '1' << std::flush;
    return utils::FileGuard{std::move(path)};
  }
};

utils::FileGuard MakeFileAndGuard(const std::string& path) {
  std::ofstream{path}.flush();
  return utils::FileGuard{path};
}

}  // namespace

TEST(OpenFilesCount, OnRemovedButOpened) {
  const utils::FileGuard directory_file{boost::filesystem::current_path() /
                                        "OpenFilesCount"};
  boost::filesystem::create_directory(directory_file.Path());

  auto temp_file =
      fs::blocking::TempFile::Create(directory_file.Path().string(), "");
  auto fd = utils::FileDescriptor::Open(
      temp_file.GetPath(), utils::FileDescriptor::OpenFlag::kWrite);
  {
    utils::FileGuard file{fd.Path()};
    EXPECT_EQ(1, testing::OpenFilesCountWithPrefix(fd.Path()))
        << "Path: " << fd.Path();
  }

  EXPECT_EQ(1, testing::OpenFilesCountWithPrefix(fd.Path()))
      << "Path: " << fd.Path();
}

UTEST(FileDetector, NoFiles) {
  FileDetectorTest test;
  FileDetector fd(dynamic_config::GetDefaultSource(), test.conf, test.db,
                  test.http, test.stats, 0);
  EXPECT_EQ(fd.FilesCount(), 0u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 0u);
  test.ExpectFileDiff(0, __LINE__);

  fd();

  EXPECT_EQ(fd.FilesCount(), 0u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 0u);
  EXPECT_EQ(test.GetFileRotationsStat(), 0u);
  test.ExpectFileDiff(0, __LINE__);
}

UTEST(FileDetector, FileAdded) {
  FileDetectorTest test;
  FileDetector fd(dynamic_config::GetDefaultSource(), test.conf, test.db,
                  test.http, test.stats, 0);
  EXPECT_EQ(fd.FilesCount(), 0u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 0u);
  EXPECT_EQ(test.GetFileRotationsStat(), 0u);
  test.ExpectFileDiff(0, __LINE__);

  utils::FileGuard file = test.Make1ByteFileAndGuard();
  fd();
  EXPECT_EQ(fd.FilesCount(), 1u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 1u);
  EXPECT_EQ(test.GetFileRotationsStat(), 0u);
  test.ExpectFileDiff(1, __LINE__);

  utils::FileGuard file2 = test.Make1ByteFileAndGuard();
  fd();
  EXPECT_EQ(fd.FilesCount(), 2u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 2u);
  EXPECT_EQ(test.GetFileRotationsStat(), 0u);
  test.ExpectFileDiff(2, __LINE__);
}

UTEST(FileDetector, FileAntique) {
  FileDetectorTest test;
  FileDetector fd(dynamic_config::GetDefaultSource(), test.conf, test.db,
                  test.http, test.stats, 0);
  EXPECT_EQ(fd.FilesCount(), 0u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 0u);
  EXPECT_EQ(test.GetFileRotationsStat(), 0u);
  test.ExpectFileDiff(0, __LINE__);

  utils::FileGuard file1 = test.Make1ByteFileAndGuard();
  fd();
  EXPECT_EQ(fd.FilesCount(), 1u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 1u);
  EXPECT_EQ(test.GetFileRotationsStat(), 0u);
  test.ExpectFileDiff(1, __LINE__);

  boost::filesystem::last_write_time(file1.Path(), std::time_t{100});
  fd();
  EXPECT_EQ(fd.FilesCount(), 0u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 0u);
  EXPECT_EQ(test.GetFileRotationsStat(), 1u);
  test.ExpectFileDiff(0, __LINE__);

  const auto now =
      std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
  boost::filesystem::last_write_time(file1.Path(), now);
  fd();
  EXPECT_EQ(fd.FilesCount(), 1u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 1u);
  EXPECT_EQ(test.GetFileRotationsStat(), 1u);
  test.ExpectFileDiff(1, __LINE__);
}

UTEST(FileDetector, FileRemoved) {
  FileDetectorTest test;
  FileDetector fd(dynamic_config::GetDefaultSource(), test.conf, test.db,
                  test.http, test.stats, 0);
  EXPECT_EQ(fd.FilesCount(), 0u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 0u);
  EXPECT_EQ(test.GetFileRotationsStat(), 0u);
  test.ExpectFileDiff(0, __LINE__);

  utils::FileGuard file1 = test.Make1ByteFileAndGuard();
  fd();
  EXPECT_EQ(fd.FilesCount(), 1u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 1u);
  EXPECT_EQ(test.GetFileRotationsStat(), 0u);
  test.ExpectFileDiff(1, __LINE__);

  {
    utils::FileGuard file2 = test.Make1ByteFileAndGuard();
    fd();
    EXPECT_EQ(fd.FilesCount(), 2u);
    EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 2u);
    EXPECT_EQ(test.GetFileRotationsStat(), 0u);
    test.ExpectFileDiff(2, __LINE__);
  }

  EXPECT_EQ(fd.FilesCount(), 2u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 2u);
  EXPECT_EQ(test.GetFileRotationsStat(), 0u);
  test.ExpectFileDiff(2, __LINE__);
  fd();
  EXPECT_EQ(fd.FilesCount(), 1u);
  EXPECT_EQ(test.stats.config_entries[0].pending_input_bytes, 1u);
  EXPECT_EQ(test.GetFileRotationsStat(), 1u);
  test.ExpectFileDiff(1, __LINE__);
}

UTEST(FileDetector, TwoPathWildcards_TAXICOMMON_520) {
  FileDetectorTest test;

  boost::filesystem::create_directory(test.directory_file.Path() / "taxi");
  const utils::FileGuard taxi_guard{test.directory_file.Path() / "taxi"};

  const auto taxi_directory = taxi_guard.Path().string();

  const utils::FileGuard guards[] = {
      MakeFileAndGuard(taxi_directory + "/a.log"),
      MakeFileAndGuard(taxi_directory + "/0server.log"),
      MakeFileAndGuard(taxi_directory + "/server.log"),  // <= matches
      MakeFileAndGuard(taxi_directory + "/server.log.1"),
      MakeFileAndGuard(taxi_directory + "/server.log.2.gz"),
      MakeFileAndGuard(taxi_directory + "/taxi.log"),  // <= matches
      MakeFileAndGuard(taxi_directory + "/taxi1.log"),
      MakeFileAndGuard(taxi_directory + "/taxi.log.1.gz"),
  };

  test.conf.input.paths.clear();
  const auto wildcard_pref = test.directory_file.Path().string() + "/taxi*/";
  test.conf.input.paths.push_back(wildcard_pref + "server.log");
  test.conf.input.paths.push_back(wildcard_pref + "taxi.log");

  FileDetector fd(dynamic_config::GetDefaultSource(), test.conf, test.db,
                  test.http, test.stats, 0);
  EXPECT_EQ(fd.FilesCount(), 0u);
  test.ExpectFileDiff(0, __LINE__);

  fd();

  EXPECT_EQ(fd.FilesCount(), 2u);
  test.ExpectFileDiff(2, __LINE__);

  fd();

  EXPECT_EQ(fd.FilesCount(), 2u);
  test.ExpectFileDiff(2, __LINE__);
}

UTEST(FileDetector, TwoPathWildcardsExact_TAXICOMMON_520) {
  FileDetectorTest test;

  const auto taxi_directory = test.directory_file.Path() / "taxi";
  boost::filesystem::create_directory(taxi_directory);
  const utils::FileGuard taxi_guard{taxi_directory};

  const auto driver_authorizer_directory =
      test.directory_file.Path() / "taxi-driver-authorizer";
  boost::filesystem::create_directory(driver_authorizer_directory);
  const utils::FileGuard da_guard{driver_authorizer_directory};

  const auto pilorama_directory = test.directory_file.Path() / "taxi-pilorama";
  boost::filesystem::create_directory(pilorama_directory);
  const utils::FileGuard pilorama_guard{pilorama_directory};

  const auto taxi_prefix = test.directory_file.Path().string() + "/taxi";

  const utils::FileGuard guards[] = {
      // does not match
      MakeFileAndGuard(taxi_prefix + "/a.log"),
      // matches
      MakeFileAndGuard(taxi_prefix + "/taxi.log"),
      // does not match
      MakeFileAndGuard(taxi_prefix + "/taxi.log.1"),

      // matches
      MakeFileAndGuard(taxi_prefix + "-driver-authorizer/server.log"),
      // does not match
      MakeFileAndGuard(taxi_prefix + "-driver-authorizer/server.log.1"),
      // does not match
      MakeFileAndGuard(taxi_prefix + "-driver-authorizer/server.log.2.gz"),

      // matches
      MakeFileAndGuard(taxi_prefix + "-pilorama/server.log"),
      // does not match
      MakeFileAndGuard(taxi_prefix + "-pilorama/server.log1.gz"),
  };

  test.conf.input.paths.clear();
  const auto wildcard_pref = test.directory_file.Path().string() + "/taxi*/";
  test.conf.input.paths.push_back(wildcard_pref + "server.log");
  test.conf.input.paths.push_back(wildcard_pref + "taxi.log");

  FileDetector fd(dynamic_config::GetDefaultSource(), test.conf, test.db,
                  test.http, test.stats, 0);
  EXPECT_EQ(fd.FilesCount(), 0u);
  test.ExpectFileDiff(0, __LINE__);

  fd();

  EXPECT_EQ(fd.FilesCount(), 3u);
  test.ExpectFileDiff(3, __LINE__);
  {
    const auto guard = MakeFileAndGuard(taxi_prefix + "-pilorama/taxi.log");
    fd();
    EXPECT_EQ(fd.FilesCount(), 4u);
    test.ExpectFileDiff(4, __LINE__);
  }

  fd();
  EXPECT_EQ(fd.FilesCount(), 3u);
  test.ExpectFileDiff(3, __LINE__);
}

// Following tests work well on local machine but may run for a very long time
// on a build server with heavy load.
//
// To enable those tests, run binary with the following additional options:
//--gtest_also_run_disabled_tests --gtest_filter=FileDetectorINode.*

struct FileDetectorINodeTest {
  FileDetectorINodeTest() { EXPECT_EQ(DetectedFilesCount(), 0u); }
  ~FileDetectorINodeTest();

  bool NotEnoughReusages() { return ids_reused < inode_reusages_required; }

  utils::FileGuard MakeFileAndDetectIt();

  void DetectFiles() { fd(); }

  std::size_t DetectedFilesCount() const;

 private:
  FileDetectorTest test;
  FileDetector fd{dynamic_config::GetDefaultSource(),
                  test.conf,
                  test.db,
                  test.http,
                  test.stats,
                  0};

  using FileId = utils::FileId;
  std::unordered_map<FileId, std::size_t, boost::hash<FileId>> ids;
  const std::size_t inode_reusages_required = 5;
  unsigned ids_reused = 0;
};

FileDetectorINodeTest::~FileDetectorINodeTest() {
  DetectFiles();
  EXPECT_EQ(DetectedFilesCount(), 0u);
}

utils::FileGuard FileDetectorINodeTest::MakeFileAndDetectIt() {
  auto file_path = utils::CreateUniqueFile(test.directory_file.Path());

  const FileId id =
      utils::FileDescriptor::Open(file_path.string(),
                                  utils::FileDescriptor::OpenFlag::kRead)
          .GetId();
  ids_reused += (ids[id]++ ? 1 : 0);

  DetectFiles();

  return utils::FileGuard{file_path};
}

std::size_t FileDetectorINodeTest::DetectedFilesCount() const {
  const auto opened =
      testing::OpenFilesCountWithPrefix(test.directory_file.Path());
  EXPECT_EQ(fd.FilesCount(), opened)
      << "Files count monitored by FileDetector missmatch open files count "
      << "for the application. "
      << "Could be an issue of FileDetector not keeping the file opened.";
  return fd.FilesCount();
}

UTEST(FileDetectorINode, DISABLED_ReuseBasic) {
  FileDetectorINodeTest test;

  while (test.NotEnoughReusages()) {
    {
      auto file = test.MakeFileAndDetectIt();
      EXPECT_EQ(test.DetectedFilesCount(), 1u);
    }

    test.DetectFiles();
    EXPECT_EQ(test.DetectedFilesCount(), 0u);
  }
}

UTEST(FileDetectorINode, DISABLED_ReuseTwoFiles) {
  FileDetectorINodeTest test;

  while (test.NotEnoughReusages()) {
    {
      auto file = test.MakeFileAndDetectIt();
      EXPECT_EQ(test.DetectedFilesCount(), 1u);

      {
        auto file = test.MakeFileAndDetectIt();
        EXPECT_EQ(test.DetectedFilesCount(), 2u);
      }

      test.DetectFiles();
      EXPECT_EQ(test.DetectedFilesCount(), 1u);
    }

    test.DetectFiles();
    EXPECT_EQ(test.DetectedFilesCount(), 0u);
  }
}

UTEST(FileDetectorINode, DISABLED_ReuseInLogRotateScenario) {
  FileDetectorINodeTest test;

  while (test.NotEnoughReusages()) {
    {
      auto file = test.MakeFileAndDetectIt();
      EXPECT_EQ(test.DetectedFilesCount(), 1u);

      boost::filesystem::remove(file.Path());
      {
        std::ofstream f{file.Path().native()};
        f.flush();
      }
      test.DetectFiles();
      EXPECT_EQ(test.DetectedFilesCount(), 1u);
    }

    test.DetectFiles();
    EXPECT_EQ(test.DetectedFilesCount(), 0u);
  }
}
