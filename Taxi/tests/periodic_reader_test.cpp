#include <atomic>
#include <fstream>

#include "file_guard.hpp"
#include "file_ops.hpp"
#include "periodic_reader.hpp"

#include <userver/engine/sleep.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <boost/filesystem/operations.hpp>

#include "open_files_count.hpp"

namespace {

constexpr auto pollingInterval = std::chrono::milliseconds(2);
constexpr auto sleepInterval = pollingInterval * 3;

constexpr std::chrono::system_clock::time_point record_time1{
    std::chrono::seconds{1532538251}};
constexpr std::chrono::system_clock::time_point record_time2{
    std::chrono::seconds{2532538252}};

using InvocationInfo = pilorama::PeriodicReader::InvocationInfo;

void AppendData(const utils::FileGuard& file, const char* data) {
  using namespace std;
  ofstream ofs{file.Path().c_str(), ios::binary | ios::out | ios::app};
  if (ofs.fail()) {
    throw std::runtime_error("Filed to open file " + file.Path().string() +
                             " in PeriodicReader tests");
  }
  ofs << data;
  LOG_DEBUG() << "PeriodicReader tests: appended data";
}

class TestFDPoll {
 public:
  void AppendData(const char* data) const { ::AppendData(file_, data); }

  void WaitForInvocations(unsigned expected_count) const {
    for (unsigned retries = 0; retries < 10 * expected_count; ++retries) {
      if (invocations_ < expected_count) {
        engine::SleepFor(sleepInterval);
      } else {
        break;
      }
    }
  }

  utils::FileDescriptor GetFD() const {
    return utils::FileDescriptor::Open(file_.Path().string(),
                                       utils::FileDescriptor::OpenFlag::kRead);
  }

  boost::filesystem::path GetPath() const { return file_.Path(); }

  void RememberInvocation() { ++invocations_; }
  unsigned GetInvocations() const { return invocations_; }

 private:
  const utils::FileGuard file_{
      utils::CreateUniqueFile(boost::filesystem::current_path())};
  unsigned invocations_ = 0;
};

template <class Callback>
pilorama::PeriodicReader MakePeriodicReader(
    utils::FileDescriptor file, Callback f, std::chrono::milliseconds interval,
    std::size_t already_consumed = 0,
    std::size_t max_read_size = 1024 * 1024 * 16) {
  return pilorama::PeriodicReader{std::move(file), std::move(f), interval,
                                  already_consumed, max_read_size};
}

struct ReadWriteData {
  explicit ReadWriteData(std::size_t data_size) : data_size_{data_size} {
    written_.reserve(data_size);
    read_.reserve(data_size);
  }

  // It is safe to do read and write appends from different threads

  void AppendRead(std::string_view data) {
    read_.append(data.begin(), data.end());
    read_size_ += data.size();  // for thread safe read_.size()
  }

  void AppendWritten(const char* data) { written_ += data; }

  void WaitForEndOfReading() {
    ASSERT_EQ(written_.size(), data_size_) << "Badly written test";

    engine::Task t = utils::Async("Busy wait for end of reading", [&] {
      while (read_size_ < data_size_) {
        engine::SleepFor(sleepInterval);
      }
    });
    t.WaitFor(utest::kMaxTestWaitTime);
  }

  const std::string& Read() const { return read_; }
  const std::string& Written() const { return written_; }

 private:
  const std::size_t data_size_;
  std::string read_{};
  std::string written_{};
  std::atomic<std::size_t> read_size_{0};
};

using Truncation = pilorama::PeriodicReader::Truncation;

}  // anonymous namespace

UTEST(PeriodicReader, ReadAllInOnce) {
  constexpr char test_data[] = "test string";

  TestFDPoll test;
  test.AppendData(test_data);

  auto reader = MakePeriodicReader(
      test.GetFD(),
      [&test, &test_data](std::string_view data, Truncation trunc) {
        EXPECT_EQ(trunc, Truncation::kNone);
        test.RememberInvocation();
        EXPECT_EQ(data, test_data) << "On iteration " << test.GetInvocations();

        return InvocationInfo{data.size(), record_time1};
      },
      pollingInterval);

  test.WaitForInvocations(1);

  // Validating that callback was not invoked any more.
  engine::SleepFor(sleepInterval);
  EXPECT_EQ(test.GetInvocations(), 1);
  EXPECT_EQ(reader.LastRecordTime(), record_time1);

  // Check that multiple Stop invocation work well.
  reader.ConsumeAllAndStop();
  reader.ConsumeAllAndStop();
}

UTEST(PeriodicReader, ReadAllInOnceWithSkip) {
  constexpr char test_data[] = "test string";
  constexpr std::size_t skip_bytes = 5;
  const char* test_data_skipped = test_data + skip_bytes;

  TestFDPoll test;
  test.AppendData(test_data);

  auto reader = MakePeriodicReader(
      test.GetFD(),
      [&test, test_data_skipped](std::string_view data, Truncation trunc) {
        EXPECT_EQ(trunc, Truncation::kNone);
        test.RememberInvocation();
        EXPECT_EQ(data, test_data_skipped)
            << "On iteration " << test.GetInvocations();

        return InvocationInfo{data.size(), record_time2};
      },
      pollingInterval, skip_bytes);

  test.WaitForInvocations(1);

  // Validating that callback was not invoked any more.
  engine::SleepFor(sleepInterval);
  EXPECT_EQ(test.GetInvocations(), 1);
  EXPECT_EQ(reader.LastRecordTime(), record_time2);
}

UTEST(PeriodicReader, ReadAndAppendOnce) {
  constexpr char test_data[] = "test string";

  TestFDPoll test;
  test.AppendData(test_data);

  auto reader = MakePeriodicReader(
      test.GetFD(),
      [&test, &test_data](std::string_view data, Truncation trunc) {
        EXPECT_EQ(trunc, Truncation::kNone);
        test.RememberInvocation();
        EXPECT_EQ(data, test_data) << "On iteration " << test.GetInvocations();
        if (1 == test.GetInvocations()) {
          test.AppendData(test_data);
        }
        return InvocationInfo{data.size(), record_time1};
      },
      pollingInterval);

  test.WaitForInvocations(2);
  EXPECT_EQ(test.GetInvocations(), 2);
}

UTEST(PeriodicReader, ReadAppendTwiceAndReadFull) {
  constexpr char test_data[] = "Testing!";
  using std::string_view;

  TestFDPoll test;
  test.AppendData(test_data);

  std::string data_written;
  auto reader = MakePeriodicReader(
      test.GetFD(),
      [&test, &data_written, &test_data](string_view data, Truncation trunc) {
        EXPECT_EQ(trunc, Truncation::kNone);
        test.RememberInvocation();
        if (test.GetInvocations() < 3) {
          test.AppendData(test_data);
        }
        if (test.GetInvocations() == 3) {
          data_written.append(data.begin(), data.end());
          return InvocationInfo{data.size(), record_time2};
        }
        return InvocationInfo{0, record_time1};
      },
      pollingInterval);

  test.WaitForInvocations(3);
  EXPECT_EQ(test.GetInvocations(), 3);
  EXPECT_EQ(reader.LastRecordTime(), record_time2);

  std::string expected = test_data;
  expected.append(test_data);
  expected.append(test_data);

  EXPECT_EQ(data_written, expected);
}

UTEST(PeriodicReader, ReadTruncateAppend) {
  constexpr char test_data[] = "Testing!";
  using std::string_view;

  TestFDPoll test;
  test.AppendData(test_data);

  std::string data_written;
  auto reader = MakePeriodicReader(
      test.GetFD(),
      [&test, &data_written, &test_data](string_view data, Truncation trunc) {
        test.RememberInvocation();
        data_written.append(data.begin(), data.end());

        switch (test.GetInvocations()) {
          case 1: {
            EXPECT_EQ(trunc, Truncation::kNone);
            boost::system::error_code err;
            boost::filesystem::resize_file(test.GetPath(), 0, err);
            EXPECT_FALSE(err) << "Error during file truncation: " << err;
            EXPECT_NE(data.size(), 0u);
            return InvocationInfo{data.size(), record_time1};
          }
          case 2: {
            EXPECT_EQ(trunc, Truncation::kDetected);
            test.AppendData(test_data);
            EXPECT_EQ(data.size(), 0u);
            return InvocationInfo{data.size(), record_time1};
          }
          case 3: {
            EXPECT_EQ(trunc, Truncation::kNone);
            EXPECT_NE(data.size(), 0u);
            return InvocationInfo{data.size(), record_time2};
          }
        }
        EXPECT_TRUE(false) << "Unexpected behavior. Callback executed more "
                              "times than expected";

        return InvocationInfo{0, record_time1};
      },
      pollingInterval);

  test.WaitForInvocations(3);
  EXPECT_EQ(test.GetInvocations(), 3);
  EXPECT_EQ(reader.LastRecordTime(), record_time2);

  std::string expected = test_data;
  expected.append(test_data);

  EXPECT_EQ(data_written, expected);
}

UTEST(PeriodicReader, ReadAppendTruncateAppend) {
  constexpr char test_data[] = "Testing!";
  using std::string_view;

  TestFDPoll test;
  test.AppendData(test_data);

  std::string data_written;
  auto reader = MakePeriodicReader(
      test.GetFD(),
      [&test, &data_written, &test_data](string_view data, Truncation trunc) {
        test.RememberInvocation();
        EXPECT_NE(data.size(), 0u);
        data_written.append(data.begin(), data.end());

        switch (test.GetInvocations()) {
          case 1: {
            EXPECT_EQ(trunc, Truncation::kNone);
            test.AppendData(test_data);
            return InvocationInfo{data.size(), record_time1};
          }
          case 2: {
            EXPECT_EQ(trunc, Truncation::kNone);
            boost::system::error_code err;
            boost::filesystem::resize_file(test.GetPath(), 0, err);
            EXPECT_FALSE(err) << "Error during file truncation: " << err;
            test.AppendData(test_data);
            return InvocationInfo{data.size(), record_time1};
          }
          case 3: {
            EXPECT_EQ(trunc, Truncation::kDetected);
            return InvocationInfo{data.size(), record_time2};
          }
        }
        EXPECT_TRUE(false) << "Unexpected behavior. Callback executed more "
                              "times than expected";

        return InvocationInfo{0, record_time1};
      },
      pollingInterval);

  test.WaitForInvocations(3);
  EXPECT_EQ(test.GetInvocations(), 3);
  EXPECT_EQ(reader.LastRecordTime(), record_time2);

  std::string expected = test_data;
  expected.append(test_data);
  expected.append(test_data);

  EXPECT_EQ(data_written, expected);
}

UTEST(PeriodicReader, ReadAndAppendCrossingPageBoundries) {
  const unsigned writes_count = 16;
  using std::string_view;

  std::string test_data(1, 'a');
  test_data.resize(1024 * 4 - 1, 'b');

  TestFDPoll test;
  test.AppendData(test_data.c_str());

  auto callback = [&test_data, &test, total_writes = writes_count](
                      string_view data, Truncation trunc) {
    EXPECT_EQ(trunc, Truncation::kNone);
    EXPECT_EQ(data, test_data) << "On iteration " << test.GetInvocations();
    test.RememberInvocation();
    if (test.GetInvocations() < total_writes) {
      test.AppendData(test_data.c_str());
    }
    return InvocationInfo{data.size(), record_time1};
  };

  auto reader =
      MakePeriodicReader(test.GetFD(), std::move(callback), pollingInterval);

  test.WaitForInvocations(writes_count);
  EXPECT_EQ(test.GetInvocations(), writes_count);
  EXPECT_EQ(reader.LastRecordTime(), record_time1);
}

// Making sure that `ConsumeAllAndStop()` finishes reading opened file
// and does not close it even if the file is removed.
UTEST(PeriodicReader, ConsumeAllAndStop) {
  constexpr char test_data[] = "test string";

  TestFDPoll test;
  test.AppendData(test_data);

  auto reader = MakePeriodicReader(
      test.GetFD(),
      [&test, &test_data](std::string_view data, Truncation trunc) {
        EXPECT_EQ(trunc, Truncation::kNone);
        test.RememberInvocation();
        switch (test.GetInvocations()) {
          case 1:
            EXPECT_EQ(data, test_data)
                << "On iteration " << test.GetInvocations();
            return InvocationInfo{0, record_time1};
          case 2:
            EXPECT_EQ(data, std::string(test_data) + test_data)
                << "On iteration " << test.GetInvocations();
            return InvocationInfo{data.size(), record_time2};
          default:
            EXPECT_TRUE(false) << "On iteration " << test.GetInvocations();
        }

        return InvocationInfo{0, record_time1};
      },
      std::chrono::minutes{15});

  test.WaitForInvocations(1);
  EXPECT_EQ(reader.LastRecordTime(), record_time1);

  const auto open_files_before_stop =
      testing::OpenFilesCountWithPrefix(test.GetPath());
  EXPECT_EQ(open_files_before_stop, 1);
  test.AppendData(test_data);

  boost::filesystem::remove(test.GetPath());
  const boost::filesystem::path replacement =
      utils::CreateUniqueFile(test.GetPath().parent_path());
  boost::filesystem::rename(replacement, test.GetPath());

  reader.ConsumeAllAndStop();
  EXPECT_EQ(test.GetInvocations(), 2);
  EXPECT_EQ(reader.LastRecordTime(), record_time2);
  EXPECT_EQ(open_files_before_stop,
            testing::OpenFilesCountWithPrefix(test.GetPath()));
}

// Making sure that calling a destructor closes file descriptor and finishes
// immediately, without processing pending bits of data.
UTEST(PeriodicReader, Destroy) {
  constexpr char test_data[] = "test string";

  TestFDPoll test;
  test.AppendData(test_data);

  auto reader = std::make_unique<pilorama::PeriodicReader>(
      test.GetFD(),
      [&test, &test_data](std::string_view data, Truncation trunc)
          -> pilorama::PeriodicReader::InvocationInfo {
        EXPECT_EQ(trunc, Truncation::kNone);
        test.RememberInvocation();
        switch (test.GetInvocations()) {
          case 1:
            EXPECT_EQ(data, test_data)
                << "On iteration " << test.GetInvocations();
            return {};
          default:
            EXPECT_TRUE(false) << "On iteration " << test.GetInvocations();
        }

        return {};
      },
      std::chrono::minutes{15}, 0, 4096);

  test.WaitForInvocations(1);

  test.AppendData(test_data);

  const auto open_files_before_destroy =
      testing::OpenFilesCountWithPrefix(test.GetPath());
  EXPECT_EQ(open_files_before_destroy, 1);
  reader.reset();
  EXPECT_EQ(test.GetInvocations(), 1);
  EXPECT_EQ(open_files_before_destroy,
            testing::OpenFilesCountWithPrefix(test.GetPath()) + 1);
}

UTEST_MT(PeriodicReader, Concurrent, 2) {
  constexpr char data_chunk[] = "0123456789a";
  constexpr std::size_t iterations = 4096;

  utils::FileGuard tmp_file{utils::CreateUniqueFile()};
  ReadWriteData test_data{(sizeof(data_chunk) - 1) * iterations};
  {
    auto reader = MakePeriodicReader(
        utils::FileDescriptor::Open(tmp_file.Path().string(),
                                    utils::FileDescriptor::OpenFlag::kRead),
        [&test_data](std::string_view data, Truncation trunc) {
          EXPECT_EQ(trunc, Truncation::kNone);
          test_data.AppendRead(data);
          return InvocationInfo{data.size(), record_time1};
        },
        pollingInterval);

    for (unsigned i = 0; i < iterations; ++i) {
      AppendData(tmp_file, data_chunk);
      test_data.AppendWritten(data_chunk);
    }

    test_data.WaitForEndOfReading();
  }
  EXPECT_EQ(test_data.Read(), test_data.Written());
}

UTEST_MT(PeriodicReader, ConcurrentWithFileMove, 2) {
  constexpr char data_chunk[] = "0123sahjhdsagajx456789a";
  constexpr std::size_t iterations = 4096;

  utils::FileGuard initial_file_path_guard{utils::CreateUniqueFile()};
  ReadWriteData test_data{(sizeof(data_chunk) - 1) * iterations};

  {
    auto reader = MakePeriodicReader(
        utils::FileDescriptor::Open(initial_file_path_guard.Path().string(),
                                    utils::FileDescriptor::OpenFlag::kRead),
        [&test_data](std::string_view data, Truncation trunc) {
          EXPECT_EQ(trunc, Truncation::kNone);
          test_data.AppendRead(data);
          return InvocationInfo{data.size(), record_time1};
        },
        pollingInterval);

    for (unsigned i = 0; i < iterations / 2; ++i) {
      AppendData(initial_file_path_guard, data_chunk);
      test_data.AppendWritten(data_chunk);
    }

    // Move old file to a new path, create a temp file and place it to
    // the old path.
    const auto initial_file_path = initial_file_path_guard.Path();
    const auto renamed_file_path = initial_file_path.string() + "_renamed";
    boost::filesystem::rename(initial_file_path, renamed_file_path);
    utils::FileGuard renamed_file_path_guard(renamed_file_path);
    const boost::filesystem::path replacement =
        utils::CreateUniqueFile(initial_file_path.parent_path());
    boost::filesystem::rename(replacement, initial_file_path);

    // Continue writing data to the renamed file
    for (unsigned i = iterations / 2; i < iterations; ++i) {
      AppendData(renamed_file_path_guard, data_chunk);
      test_data.AppendWritten(data_chunk);
    }

    test_data.WaitForEndOfReading();
  }
  EXPECT_EQ(test_data.Read(), test_data.Written());
}

UTEST_MT(PeriodicReader, ConcurrentWithFileRemove, 2) {
  constexpr char data_chunk[] = "0123sahjhdsagajx456789a";
  constexpr std::size_t iterations = 4096;

  utils::FileGuard initial_file_path_guard{utils::CreateUniqueFile()};
  ReadWriteData test_data{(sizeof(data_chunk) - 1) * iterations};
  {
    auto reader = MakePeriodicReader(
        utils::FileDescriptor::Open(initial_file_path_guard.Path().string(),
                                    utils::FileDescriptor::OpenFlag::kRead),
        [&test_data](std::string_view data, Truncation trunc) {
          EXPECT_EQ(trunc, Truncation::kNone);
          test_data.AppendRead(data);
          return InvocationInfo{data.size(), record_time1};
        },
        pollingInterval * 100  // Big interval to provoke reading removed file
    );

    for (unsigned i = 0; i < iterations; ++i) {
      AppendData(initial_file_path_guard, data_chunk);
      test_data.AppendWritten(data_chunk);
    }

    // Remove file and make a new one.
    boost::filesystem::remove(initial_file_path_guard.Path());
    const boost::filesystem::path replacement =
        utils::CreateUniqueFile(initial_file_path_guard.Path().parent_path());
    boost::filesystem::rename(replacement, initial_file_path_guard.Path());

    test_data.WaitForEndOfReading();
  }
  EXPECT_EQ(test_data.Read(), test_data.Written());
}
