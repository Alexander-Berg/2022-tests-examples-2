#include "pilorama.hpp"

#include <fstream>
#include <list>

#include <boost/filesystem/operations.hpp>

#include <testing/taxi_config.hpp>
#include <userver/engine/sleep.hpp>
#include <userver/engine/task/task.hpp>
#include <userver/formats/json.hpp>
#include <userver/fs/blocking/read.hpp>
#include <userver/fs/blocking/temp_directory.hpp>
#include <userver/fs/blocking/temp_file.hpp>
#include <userver/logging/log.hpp>
#include <userver/storages/secdist/component.hpp>
#include <userver/utest/http_client.hpp>
#include <userver/utest/simple_server.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

#include <taxi_config/variables/PILORAMA_PROCESSING_OVERRIDES.hpp>

#include "file_guard.hpp"

namespace {

constexpr char kRecord[] =
    "tskv\ttimestamp=2018-07-25 17:04:11,890542\tmodule=operator() ( "
    "common/src/threads/thread_pool_monitor.cpp:96 "
    ")\tlevel=INFO\tthread=7f247cd45700\tlink=None\tpool_name=clients_http_"
    "pool\texecution_delay_time=0.016813\t_type=log\ttext=\t\n";

constexpr std::size_t kRecordBytes = sizeof(kRecord) - 1;

constexpr char kJsonRecord[] =
    R"olo({"timestamp":"2018-07-25 17:04:11,890542",)olo"
    R"olo("module":"operator() ( common/src/threads/thread_pool_monitor.cpp:96 )",)olo"
    R"olo("level":"INFO","thread":"7f247cd45700","link":"None",)olo"
    R"olo("pool_name":"clients_http_pool","execution_delay_time":"0.016813",)olo"
    R"olo("_type":"log","text":"hello"})olo"
    "\n";

constexpr char kTskvJaegerSpan[] =
    "tskv\ttrace_id=ed6a3545c9ac4651a6b3f9b3281b5e88"
    "\tspan_id=3c4283d0afc94d41b89f71373871cb53"
    "\tparent_id=7668a0239eb641a69bf83980116e3423"
    "\toperation_name=Distlock db operations"
    "\tduration=11"
    "\tstart_time=1581064128321122"
    "\tstart_time_millis=1581064128321\n";

const std::string kJaegerFilterConfig = R"=(
          filter:
            transform_date: false
            drop_empty_fields: true
            put_message: false
            start_message_from_tskv: true
            renames:
              - from: trace_id
                to: traceID
              - from: span_id
                to: spanID
              - from: start_time
                to: startTime
              - from: start_time_millis
                to: startTimeMillis
              - from: operation_name
                to: operationName
            additions:
              - '"flags":1'
            minimal_log_level: info
            input_format: tskv-jaeger-span)=";

const std::string kJaegerServiceIndex = "jaeger_service_index: jaeger-service";

constexpr std::size_t kJaegerRecordBytes = sizeof(kTskvJaegerSpan) - 1;

constexpr std::size_t kJsonRecordBytes = sizeof(kJsonRecord) - 1;

constexpr const char* kSingleRecordToIgnore =
    "tskv"
    "\ttimestamp=2019-07-25 17:44:11,890542"
    "\tmodule=operator() ( nonesuch.cpp:96 )"
    "\tlevel=INFO"
    "\tlink=42"
    "\tpool_name=clients_http_pool"
    "\texecution_delay_time=0.016813"
    "\t_type=log"
    "\ttext="
    " And the Raven, never flitting, still is sitting, still is sitting    "
    " On the pallid bust of Pallas just above my chamber door;             "
    " And his eyes have all the seeming of a demon's that is dreaming,     "
    " And the lamp-light o'er him streaming throws his shadow on the floor;"
    " And my soul from out that shadow that lies floating on the floor     "
    "             Shall be lifted-nevermore!                               "
    "\t\n";

static const std::size_t kIgnoredRecordsCount = 1024;  // 2^10
const char* RecordsToIgnore() {
  static const auto res = []() {
    std::string result = kSingleRecordToIgnore;
    result.reserve(result.size() * kIgnoredRecordsCount);
    for (unsigned i = 0; i < 10; ++i) result += result;
    return result;
  }();

  return res.c_str();
}
static const std::size_t kIgnoredRecordBytes = std::strlen(RecordsToIgnore());

struct PiloramaTest {
  static constexpr std::chrono::milliseconds kPiloramaDiscoverInterval{500};
  static constexpr std::chrono::milliseconds kPiloramaSendTimeout{25};

  const fs::blocking::TempFile sync_db_file = fs::blocking::TempFile::Create();
  const fs::blocking::TempFile monitor_file = fs::blocking::TempFile::Create();
  const fs::blocking::TempFile config_file = fs::blocking::TempFile::Create();
  const fs::blocking::TempDirectory custom_config_dir =
      fs::blocking::TempDirectory::Create();
  const std::shared_ptr<clients::http::Client> http_client_ptr =
      utest::CreateHttpClient();
  clients::http::Client& http_client = *http_client_ptr;
  std::list<utest::SimpleServer> http_servers;

  using HttpResponse = utest::SimpleServer::Response;
  using HttpRequest = utest::SimpleServer::Request;
  using HttpCallback = utest::SimpleServer::OnRequest;

  static HttpResponse ok_callback(const HttpRequest& request) {
    LOG_INFO() << "HTTP Server receive: " << request;

    const bool requires_continue =
        (request.find("Expect: 100-continue") != std::string::npos);

    if (requires_continue || request.empty()) {
      return {
          "HTTP/1.1 100 Continue\r\nContent-Length: "
          "0\r\n\r\n",
          HttpResponse::kWriteAndContinue};
    }

    bool met_the_test_data =
        (request.find("common/src/threads/thread_pool_monitor.cpp:96") !=
         std::string::npos);
    if (!met_the_test_data) {
      met_the_test_data = request.find("operationName") != std::string::npos;
    }
    EXPECT_TRUE(met_the_test_data)
        << "Not all the required data was met in request:\n"
        << request;

    return {
        "HTTP/1.1 200 OK\r\nConnection: close\r\rContent-Length: "
        "0\r\n\r\n",
        HttpResponse::kWriteAndClose};
  }

  static HttpResponse server_down_callback(const HttpRequest& request) {
    LOG_INFO() << "HTTP Server receive: " << request;
    return {
        "HTTP/1.1 520 Web Server Is Down\r\nConnection: "
        "close\r\rContent-Length: "
        "0\r\n\r\n",
        HttpResponse::kWriteAndClose};
  }

  static HttpResponse assert_not_called(const HttpRequest& request) {
    EXPECT_TRUE(request.empty()) << "HTTP Server received: " << request;
    return {
        "HTTP/1.1 200 OK\r\nConnection: close\r\rContent-Length: "
        "0\r\n\r\n",
        HttpResponse::kWriteAndClose};
  }

  static std::string InputFormatToText(pilorama::InputFormats format) {
    switch (format) {
      case pilorama::InputFormats::kJson:
        return "json";
      case pilorama::InputFormats::kTskv:
        return "tskv";
      case pilorama::InputFormats::kTskvJaegerSpan:
        return "tskv-jaeger-span";
    }
  }

  PiloramaTest(bool start_from_begin = true, std::size_t ports_count = 2,
               HttpCallback f = ok_callback,
               pilorama::InputFormats format = pilorama::InputFormats::kTskv)
      : http_servers{} {
    while (ports_count--) {
      http_servers.emplace_back(f);
    }

    std::ofstream ofs{config_file.GetPath().c_str()};
    if (ofs.fail()) {
      throw std::runtime_error("Failed to open for writing config file " +
                               config_file.GetPath());
    }
    ofs << R"(
        - file:
           path: [)"
        << monitor_file.GetPath() << ',' << monitor_file.GetPath() + "_renamed"
        << R"(]
           sincedb_path: )"
        << sync_db_file.GetPath() << R"(
           discover_interval: )"
        << kPiloramaDiscoverInterval.count() << R"(ms
           start_from_begin: )"
        << (start_from_begin ? "true" : "false") << R"(
          filter:
            input_format: )"
        << InputFormatToText(format) << R"(
          output:
            index: testing
            max_retries: 200
            send_timeout: )"
        << kPiloramaSendTimeout.count()
        << R"(ms
            hosts:)"
           "\n";

    for (const auto& serv : http_servers) {
      ofs << "                - " << serv.GetBaseUrl() << '\n';
    }

    // Giving a few milliseconds for the CURL to finish initialization.
    engine::SleepFor(std::chrono::milliseconds(10));
  }

  PiloramaTest(const std::string& filter_config,
               const std::string& output_config_addition,
               bool start_from_begin = true, std::size_t ports_count = 2,
               HttpCallback f = ok_callback)
      : http_servers{} {
    while (ports_count--) {
      http_servers.emplace_back(f);
    }

    std::ofstream ofs{config_file.GetPath().c_str()};
    if (ofs.fail()) {
      throw std::runtime_error("Failed to open for writing config file " +
                               config_file.GetPath());
    }
    ofs << R"(
        - file:
           path: [)"
        << monitor_file.GetPath() << ',' << monitor_file.GetPath() + "_renamed"
        << R"(]
           sincedb_path: )"
        << sync_db_file.GetPath() << R"(
           discover_interval: )"
        << kPiloramaDiscoverInterval.count() << R"(ms
           start_from_begin: )"
        << (start_from_begin ? "true" : "false") << filter_config << R"(
          output:
            index: testing
            max_retries: 200
            send_timeout: )"
        << kPiloramaSendTimeout.count() << "ms";
    if (!output_config_addition.empty()) {
      ofs << R"(
            )"
          << output_config_addition;
    }
    ofs << R"(
            hosts:)"
           "\n";

    for (const auto& serv : http_servers) {
      ofs << "                - " << serv.GetBaseUrl() << '\n';
    }

    // Giving a few milliseconds for the CURL to finish initialization.
    engine::SleepFor(std::chrono::milliseconds(10));
  }

  void AppendData(const char* data = kRecord) {
    using namespace std;
    ofstream os{monitor_file.GetPath(), ios::binary | ios::out | ios::app};
    if (os.fail()) {
      throw std::runtime_error("Filed to open file " + monitor_file.GetPath() +
                               " in PeriodicReader tests");
    }
    os << data;
  }

  utils::FileId MonitorFileId() const {
    return utils::FileDescriptor::Open(monitor_file.GetPath(),
                                       utils::FileDescriptor::OpenFlag::kRead)
        .GetId();
  }

  void WaitFileProcessing() {
    engine::Yield();  // Start FileDetector
    engine::Yield();  // Start Syncer
    engine::Yield();  // FileDetector starts PeriodicReader
    engine::Yield();  // PeriodicReader starts NewBytesProcessor
    engine::Yield();  // NewBytesProcessor starts sending

    engine::Yield();  // NewBytesProcessor sends Error HTTP request
    engine::SleepFor(PiloramaTest::kPiloramaSendTimeout);

    engine::Yield();  // NewBytesProcessor sends Full HTTP request
    engine::SleepFor(PiloramaTest::kPiloramaSendTimeout);

    engine::Yield();  // NewBytesProcessor waits for previous Task to finish
    engine::Yield();  // NewBytesProcessor commits SyncDB
  }

  template <class Predicate>
  void Wait(Predicate pred) {
    engine::Task t = utils::Async("Busy wait for test predicate", [&] {
      while (!pred()) {
        WaitFileProcessing();
      }
    });
    t.WaitFor(utest::kMaxTestWaitTime);
    ASSERT_TRUE(pred()) << "Failed to wait for predicate";
  }

  std::string ConfigFile() const { return config_file.GetPath(); }
  std::string CustomConfigDir() const { return custom_config_dir.GetPath(); }

  void AssertCommitedBytes(std::size_t expected_bytes,
                           int invocation_number = 1) {
    pilorama::syncdb::SyncDb db(sync_db_file.GetPath());
    ASSERT_TRUE(db.GetBytesProcessed(MonitorFileId()))
        << "In AssertCommitedBytes() invocation number " << invocation_number;
    EXPECT_EQ(*db.GetBytesProcessed(MonitorFileId()), expected_bytes)
        << "In AssertCommitedBytes() invocation number " << invocation_number;
  }

  dynamic_config::StorageMock NewConfigWithLimit(std::size_t per_core_kbs,
                                                 bool is_enabled = true) const {
    auto config_storage = dynamic_config::MakeDefaultStorage({});
    const auto default_config = config_storage.GetSnapshot();

    auto conf = default_config[taxi_config::PILORAMA_PROCESSING_OVERRIDES];
    auto& file_conf = conf.skips.extra[monitor_file.GetPath()];
    file_conf.enabled = is_enabled;
    file_conf.transmission_limit_per_core_kbs = per_core_kbs;

    config_storage.Extend({{taxi_config::PILORAMA_PROCESSING_OVERRIDES, conf}});
    return config_storage;
  }
};

void TestNonEmpySendStats(const pilorama::Statistics& stats,
                          std::size_t bytes_of_input,
                          std::size_t processed_input_records = 1) {
  EXPECT_EQ(stats.config_entries[0].pending_input_bytes, 0);
  EXPECT_EQ(stats.config_entries[0].pending_input_start_ts.Load(),
            std::chrono::system_clock::duration::max());
  EXPECT_EQ(stats.processed_input_bytes, bytes_of_input);
  EXPECT_EQ(stats.processed_input_records, processed_input_records);
  EXPECT_EQ(stats.skipped_input_bytes, 0);
  EXPECT_EQ(stats.skipped_newlines, 0);
  EXPECT_GT(stats.produced_bytes, 0);
  EXPECT_EQ(stats.file_rotations, 0);

  EXPECT_EQ(stats.lost_total.bytes, 0);
  EXPECT_EQ(stats.lost_total.batches, 0);
  EXPECT_GT(stats.sent_total.bytes, stats.produced_bytes * stats.retries_all);
  EXPECT_GE(stats.sent_total.batches, 1);
}

}  // namespace

UTEST(Pilorama, NoStart) {
  PiloramaTest test;
  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);

  test.WaitFileProcessing();
}

UTEST(Pilorama, StartStopOnEmpty) {
  PiloramaTest test;

  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();

  const auto& stats = pilorama.GetStatistics();
  EXPECT_EQ(stats.config_entries[0].pending_input_bytes, 0);
  EXPECT_EQ(stats.config_entries[0].pending_input_start_ts.Load(),
            std::chrono::system_clock::duration::max());
  EXPECT_EQ(stats.processed_input_bytes, 0);
  EXPECT_EQ(stats.processed_input_records, 0);
  EXPECT_EQ(stats.skipped_input_bytes, 0);
  EXPECT_EQ(stats.skipped_newlines, 0);
  EXPECT_EQ(stats.produced_bytes, 0);
  EXPECT_EQ(stats.file_rotations, 0);
  EXPECT_EQ(stats.retries_all, 0);
  EXPECT_EQ(stats.retries_dead_remote, 0);

  EXPECT_EQ(stats.lost_total.bytes, 0);
  EXPECT_EQ(stats.lost_total.batches, 0);
  EXPECT_EQ(stats.sent_total.bytes, 0);
  EXPECT_EQ(stats.sent_total.batches, 0);

  EXPECT_EQ(stats.dropped_by_limit_bytes, 0);

  test.AssertCommitedBytes(0);
}

UTEST(Pilorama, StartWithDataInFile) {
  PiloramaTest test;
  test.AppendData();

  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.Wait([&] {
    return pilorama.GetStatistics().sent_total.batches >= 1 &&
           !pilorama.GetStatistics().config_entries[0].pending_input_bytes;
  });
  pilorama.Stop();

  TestNonEmpySendStats(pilorama.GetStatistics(), kRecordBytes);

  test.AssertCommitedBytes(kRecordBytes);

  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();

  test.AssertCommitedBytes(kRecordBytes, 2);
}

UTEST(Pilorama, StartWithJsonDataInFile) {
  PiloramaTest test{true, 2, PiloramaTest::ok_callback,
                    pilorama::InputFormats::kJson};
  test.AppendData(kJsonRecord);

  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.Wait([&] {
    return pilorama.GetStatistics().sent_total.batches >= 1 &&
           !pilorama.GetStatistics().config_entries[0].pending_input_bytes;
  });
  pilorama.Stop();

  TestNonEmpySendStats(pilorama.GetStatistics(), kJsonRecordBytes);

  test.AssertCommitedBytes(kJsonRecordBytes);

  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();

  test.AssertCommitedBytes(kJsonRecordBytes, 2);
}

UTEST(Pilorama, IncompleteRecord) {
  PiloramaTest test;
  test.AppendData();
  constexpr char kAdditionalBytes[] = "tskv\t";
  test.AppendData(kAdditionalBytes);

  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.Wait([&] {
    return pilorama.GetStatistics().sent_total.batches >= 1 &&
           pilorama.GetStatistics().config_entries[0].pending_input_bytes ==
               sizeof(kAdditionalBytes) - 1;
  });
  pilorama.Stop();

  const auto& stats = pilorama.GetStatistics();
  EXPECT_EQ(stats.config_entries[0].pending_input_bytes,
            sizeof(kAdditionalBytes) - 1);
  EXPECT_GT(std::chrono::system_clock::now().time_since_epoch() -
                stats.config_entries[0].pending_input_start_ts.Load(),
            std::chrono::seconds{1000});
  EXPECT_EQ(stats.processed_input_bytes, kRecordBytes);
  EXPECT_EQ(stats.processed_input_records, 1);
  EXPECT_EQ(stats.skipped_input_bytes, 0);
  EXPECT_EQ(stats.skipped_newlines, 0);
  EXPECT_GT(stats.produced_bytes, 0);
  EXPECT_EQ(stats.file_rotations, 0);

  EXPECT_EQ(stats.lost_total.bytes, 0);
  EXPECT_EQ(stats.lost_total.batches, 0);
  EXPECT_GT(stats.sent_total.bytes, stats.produced_bytes * stats.retries_all);
  EXPECT_GE(stats.sent_total.batches, 1);

  test.AssertCommitedBytes(kRecordBytes);
}

UTEST(Pilorama, StartWithTskvJaegerSpanInFile) {
  PiloramaTest test{kJaegerFilterConfig, kJaegerServiceIndex};
  test.AppendData(kTskvJaegerSpan);
  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.Wait([&] {
    return pilorama.GetStatistics().sent_total.batches >= 2 &&
           !pilorama.GetStatistics().config_entries[0].pending_input_bytes;
  });
  pilorama.Stop();
  TestNonEmpySendStats(pilorama.GetStatistics(), kJaegerRecordBytes);

  test.AssertCommitedBytes(kJaegerRecordBytes);

  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();

  test.AssertCommitedBytes(kJaegerRecordBytes, 2);
}

UTEST(Pilorama, JaegerSpanIncompleteRecord) {
  PiloramaTest test{kJaegerFilterConfig, kJaegerServiceIndex};
  test.AppendData(kTskvJaegerSpan);
  constexpr char kAdditionalBytes[] = "tskv\t";
  test.AppendData(kAdditionalBytes);

  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.Wait([&] {
    return pilorama.GetStatistics().sent_total.batches >= 2 &&
           pilorama.GetStatistics().config_entries[0].pending_input_bytes ==
               sizeof(kAdditionalBytes) - 1;
  });
  pilorama.Stop();

  const auto& stats = pilorama.GetStatistics();
  EXPECT_EQ(stats.config_entries[0].pending_input_bytes,
            sizeof(kAdditionalBytes) - 1);
  EXPECT_EQ(stats.config_entries[0].pending_input_start_ts.Load(),
            std::chrono::system_clock::duration::max());
  EXPECT_EQ(stats.processed_input_bytes, kJaegerRecordBytes);
  EXPECT_EQ(stats.processed_input_records, 1);
  EXPECT_EQ(stats.skipped_input_bytes, 0);
  EXPECT_EQ(stats.skipped_newlines, 0);
  EXPECT_GT(stats.produced_bytes, 0);
  EXPECT_EQ(stats.file_rotations, 0);

  EXPECT_EQ(stats.lost_total.bytes, 0);
  EXPECT_EQ(stats.lost_total.batches, 0);
  EXPECT_GT(stats.sent_total.bytes, stats.produced_bytes * stats.retries_all);
  EXPECT_GE(stats.sent_total.batches, 1);

  test.AssertCommitedBytes(kJaegerRecordBytes);
}

UTEST(Pilorama, StartWithDataInFileAndDeadServers) {
  PiloramaTest test{true, 2, PiloramaTest::server_down_callback};
  test.AppendData();

  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.Wait([&] { return pilorama.GetStatistics().retries_dead_remote != 0; });
  pilorama.Stop();

  const auto& stats = pilorama.GetStatistics();
  EXPECT_EQ(stats.processed_input_bytes, kRecordBytes);
  EXPECT_EQ(stats.processed_input_records, 1);
  EXPECT_EQ(stats.skipped_input_bytes, 0);
  EXPECT_EQ(stats.skipped_newlines, 0);
  EXPECT_GE(stats.produced_bytes, kRecordBytes);
  EXPECT_EQ(stats.file_rotations, 0);
  EXPECT_GT(stats.retries_all, 0);
  EXPECT_GT(stats.retries_dead_remote, 0);

  EXPECT_EQ(stats.lost_total.bytes, 0);
  EXPECT_EQ(stats.lost_total.batches, 0);
  EXPECT_GT(stats.sent_total.bytes, 0);
  EXPECT_GT(stats.sent_total.batches, 0);

  test.AssertCommitedBytes(0);

  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();
  test.AssertCommitedBytes(0, 2);
}

// This test makes sure that all the cancellations work right and do not throw
// from desctructors and that tasks are destroyed after the resources they use.
UTEST(Pilorama, DestroyWithActiveTasksWaiting) {
  std::unique_ptr<pilorama::Pilorama> p;
  bool terminated = false;

  auto terminator = [&p, &terminated](const PiloramaTest::HttpRequest& r) {
    EXPECT_FALSE(terminated) << "Multiple terminations, request:" << r;
    p.reset();
    terminated = true;

    return PiloramaTest::HttpResponse{
        "", PiloramaTest::HttpResponse::kWriteAndClose};
  };

  PiloramaTest test{true, 3, terminator};
  test.AppendData();

  p = std::make_unique<pilorama::Pilorama>(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  EXPECT_FALSE(terminated) << "Terminated before started";
  p->Start();

  const auto start = std::chrono::system_clock::now();
  while (!terminated) {
    engine::Yield();
  }
  const auto end = std::chrono::system_clock::now();
  EXPECT_LE(end - start, std::chrono::seconds{5})
      << "Took too long to terminate pilorama";
}

UTEST(Pilorama, StartFromEndWithDataInFile) {
  PiloramaTest test{false, 2, PiloramaTest::assert_not_called};
  test.AppendData();

  boost::filesystem::remove(test.sync_db_file.GetPath());
  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();

  test.AssertCommitedBytes(kRecordBytes);

  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();
  test.AssertCommitedBytes(kRecordBytes, 2);
}

UTEST(Pilorama, AppendDataAndNewFile) {
  PiloramaTest test;
  test.AppendData();

  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.WaitFileProcessing();
  const auto first_file_id = test.MonitorFileId();

  test.AppendData();  // first file
  test.AppendData();  // first file

  const auto renamed_file_name = test.monitor_file.GetPath() + "_renamed";
  boost::filesystem::rename(test.monitor_file.GetPath(), renamed_file_name);
  utils::FileGuard renamed_guard(renamed_file_name);

  const auto replacement = fs::blocking::TempFile::Create(
      boost::filesystem::path{test.monitor_file.GetPath()}
          .parent_path()
          .string(),
      "");
  boost::filesystem::rename(replacement.GetPath(), test.monitor_file.GetPath());

  const auto second_file_id = test.MonitorFileId();
  test.AppendData();  // second file

  test.Wait([&] {
    auto& sync_db = pilorama.GetSyncDb(test.sync_db_file.GetPath());
    const auto first = sync_db.GetBytesProcessed(first_file_id).value_or(0);
    const auto second = sync_db.GetBytesProcessed(second_file_id).value_or(0);
    return first >= kRecordBytes * 3 && second >= kRecordBytes;
  });
  pilorama.Stop();

  {
    pilorama::syncdb::SyncDb db(test.sync_db_file.GetPath());
    ASSERT_TRUE(db.GetBytesProcessed(first_file_id));
    EXPECT_EQ(*db.GetBytesProcessed(first_file_id), kRecordBytes * 3);

    ASSERT_TRUE(db.GetBytesProcessed(second_file_id));
    EXPECT_EQ(*db.GetBytesProcessed(second_file_id), kRecordBytes);
  }

  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();

  pilorama::syncdb::SyncDb db(test.sync_db_file.GetPath());
  ASSERT_TRUE(db.GetBytesProcessed(first_file_id));
  EXPECT_EQ(db.GetBytesProcessed(first_file_id), kRecordBytes * 3);

  ASSERT_TRUE(db.GetBytesProcessed(second_file_id));
  EXPECT_EQ(db.GetBytesProcessed(second_file_id), kRecordBytes);
}

UTEST(Pilorama, ReadingWithDefaultConfig) {
  PiloramaTest test;
  test.AppendData();

  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.Wait([&] {
    return pilorama.GetStatistics().sent_total.batches >= 1 &&
           !pilorama.GetStatistics().config_entries[0].pending_input_bytes;
  });

  EXPECT_DOUBLE_EQ(
      pilorama.GetStatistics().produced_bytes_1min.GetStatsForPeriod(), 0.0);
  pilorama.Stop();

  TestNonEmpySendStats(pilorama.GetStatistics(), kRecordBytes);

  test.AssertCommitedBytes(kRecordBytes);

  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();

  test.AssertCommitedBytes(kRecordBytes, 2);
  EXPECT_EQ(pilorama.GetStatistics().dropped_by_limit_bytes, 0);
}

UTEST(Pilorama, ReadingLimitIsHit) {
  PiloramaTest test;
  test.AppendData();
  test.AppendData(RecordsToIgnore());

  const auto config = test.NewConfigWithLimit(1);
  pilorama::Pilorama pilorama(
      config.GetSource(), storages::secdist::SecdistConfig(), test.ConfigFile(),
      test.CustomConfigDir(), test.http_client, nullptr);
  pilorama.Start();
  test.Wait([&] {
    return pilorama.GetStatistics().sent_total.batches >= 1 &&
           !pilorama.GetStatistics().config_entries[0].pending_input_bytes;
  });
  pilorama.Stop();

  TestNonEmpySendStats(pilorama.GetStatistics(),
                       kRecordBytes + kIgnoredRecordBytes,
                       kIgnoredRecordsCount + 1);

  test.AssertCommitedBytes(kRecordBytes + kIgnoredRecordBytes);

  pilorama.Start();
  test.WaitFileProcessing();
  pilorama.Stop();

  test.AssertCommitedBytes(kRecordBytes + kIgnoredRecordBytes, 2);
  EXPECT_GT(pilorama.GetStatistics().dropped_by_limit_bytes,
            kIgnoredRecordBytes);
}

UTEST(Pilorama, ReadingLimitIsHitLinkRemembered) {
  PiloramaTest test;
  test.AppendData(RecordsToIgnore());

  const auto config = test.NewConfigWithLimit(1);
  pilorama::Pilorama pilorama(
      config.GetSource(), storages::secdist::SecdistConfig(), test.ConfigFile(),
      test.CustomConfigDir(), test.http_client, nullptr);
  const auto& stats = pilorama.GetStatistics();
  pilorama.Start();
  test.Wait([&] {
    return stats.dropped_by_limit_bytes > kRecordBytes + kIgnoredRecordBytes &&
           !stats.config_entries[0].pending_input_bytes;
  });
  EXPECT_EQ(stats.sent_total.batches, 0);

  const auto dropped_bytes0 = stats.dropped_by_limit_bytes.Load();

  test.AppendData(RecordsToIgnore());
  test.AppendData();

  test.Wait([&] {
    return pilorama.GetStatistics().sent_total.batches >= 1 &&
           !pilorama.GetStatistics().config_entries[0].pending_input_bytes;
  });
  EXPECT_GE(stats.sent_total.batches, 1);
  EXPECT_EQ(stats.dropped_by_limit_bytes.Load(), dropped_bytes0 * 2);

  test.AppendData(kSingleRecordToIgnore);

  test.Wait([&] {
    return stats.dropped_by_limit_bytes >=
               dropped_bytes0 * 2 + std::strlen(kSingleRecordToIgnore) &&
           !stats.config_entries[0].pending_input_bytes;
  });
  ASSERT_EQ(stats.sent_total.batches, 1) << "Oops! Data was sent";
}

UTEST(Pilorama, CorrectStartAccessPermissions) {
  PiloramaTest test;
  test.AppendData();

  pilorama::Pilorama pilorama(
      dynamic_config::GetDefaultSource(), storages::secdist::SecdistConfig(),
      test.ConfigFile(), test.CustomConfigDir(), test.http_client, nullptr);

  namespace fs = boost::filesystem;
  auto cache_dir = fs::path(test.sync_db_file.GetPath()).parent_path();
  auto old_permissions = fs::status(cache_dir).permissions();
  fs::permissions(cache_dir, fs::perms::owner_read);

  EXPECT_THROW(pilorama.Start(), std::runtime_error);

  fs::permissions(cache_dir, old_permissions);
}
