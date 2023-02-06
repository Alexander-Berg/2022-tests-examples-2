#include "load_config.hpp"

#include "log_name_to_level.hpp"

#include <boost/filesystem/path.hpp>
#include <fstream>
#include <sstream>

#include <gtest/gtest.h>

#include <userver/fs/blocking/temp_directory.hpp>
#include <userver/fs/blocking/temp_file.hpp>

namespace {
struct ExceptionCheck {
  const char* const name;
  const char* const message;
  const char* const config;
};

inline std::string PrintToString(const ExceptionCheck& d) { return d.name; }

using ExceptionCheckData = std::initializer_list<ExceptionCheck>;

struct TestnameFilename {
  const char* const testname;
  const char* const filename;
};

inline std::string PrintToString(const TestnameFilename& d) {
  return d.testname;
}

using TestnameFilenameData = std::initializer_list<TestnameFilename>;

}  // namespace

TEST(ConfigsLoading, Minimal) {
  std::istringstream iss{R"(
    - file:
       path: "/test_path/debug.log"
       sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter:
      output:
       hosts: localhost:9200
    )"};

  auto configs = pilorama::LoadConfigHelper(iss);
  EXPECT_TRUE(configs.size() == 1);
}

TEST(ConfigsLoading, ReadIntervalLessThanMinimal) {
  std::istringstream iss{R"(
    - file:
        path: "/test_path/debug.log"
        sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
        read_interval: 10ms
      filter:
      output:
        hosts: localhost:9200
  )"};

  EXPECT_ANY_THROW(pilorama::LoadConfigHelper(iss));
}

TEST(ConfigsLoading, DiscoverIntervalLessThanMinimal) {
  std::istringstream iss{R"(
      - file:
          path: "/test_path/debug.log"
          sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
          discover_interval: 0s
        filter:
        output:
          hosts: localhost:9200
    )"};

  EXPECT_ANY_THROW(pilorama::LoadConfigHelper(iss));
}

TEST(ConfigsLoading, Input) {
  std::istringstream iss{R"(
    - file:
        path: "/test_path/debug.log"
        sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
        start_from_begin: true
        ignore_older: 86400
        discover_interval: 5
      output:
        hosts: localhost:9200

    - file:
        path: ['/test_path/release.log','/test_path/release.old.*.log']
        sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      output:
          hosts: localhost:9200
  )"};

  auto configs = pilorama::LoadConfigHelper(iss);
  ASSERT_EQ(configs.size(), 2u);

  const pilorama::FileConfig& debug = configs[0].input;
  ASSERT_EQ(debug.paths.size(), 1u);
  EXPECT_EQ(debug.paths[0], "/test_path/debug.log");

  const pilorama::FileConfig& release = configs[1].input;
  ASSERT_EQ(release.paths.size(), 2u);
  EXPECT_EQ(release.paths[0], "/test_path/release.log");
  EXPECT_EQ(release.paths[1], "/test_path/release.old.*.log");
}

TEST(ConfigsLoading, Filter) {
  std::istringstream iss{R"(
    - file:
          path: "/test_path/debug.log"
          sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter: &debug
          transform_date: false
          drop_empty_fields: false
          put_message: true
          start_message_from_tskv: false
          removals: ["metadata", "timestamp"]
          defaults:
            - key: foo
              value: log
          renames:
            - from: _type
              to: type
            - from: _something
              to: something_other
      output: &out
          hosts: localhost:9200

    - file:
          path: ["/test_path/release.log", "/test_path/release.old.*.log"]
          sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter: &release
          timestamp_key: unixtime
          transform_date: true
          drop_empty_fields: true
          time_formats: "%Y-%m-%dT%H:%M:%S.%E*f"
          put_message: false
          removals: "metadata"
          additions: '"tags":["_logstash_parsed"]'
          minimal_log_level: Warning
          defaults:
            - key: type
              value: log
          renames:
            - from: _type
              to: type
            - from: _something
              to: something_other
          max_read_size: 100500
          escaping: simple-escape-bypass
          input_format: json
      output: *out
  )"};

  auto configs = pilorama::LoadConfigHelper(iss);
  ASSERT_EQ(configs.size(), 2u);

  const pilorama::FilterConfig& debug = configs[0].filter;
  EXPECT_EQ(debug.timestamp_key, "timestamp");
  EXPECT_FALSE(debug.transform_date);
  EXPECT_FALSE(debug.drop_empty_fields);
  EXPECT_TRUE(debug.put_message);
  EXPECT_EQ(debug.minimal_log_level, pilorama::LogLevel::kTrace);
  EXPECT_FALSE(debug.start_message_from_tskv);
  EXPECT_EQ(debug.removals.size(), 2u);
  EXPECT_TRUE(debug.removals.count("metadata"));
  EXPECT_TRUE(debug.removals.count("timestamp"));
  EXPECT_TRUE(debug.renames.at("_type") == "type");
  ASSERT_EQ(debug.defaults.size(), 1);
  ASSERT_EQ(debug.defaults.count("foo"), 1);
  EXPECT_EQ(debug.defaults.at("foo"), "log");
  EXPECT_TRUE(debug.renames.at("_something") == "something_other");
  EXPECT_FALSE(debug.additions.find("\"cgroups\":") != std::string::npos);
  EXPECT_FALSE(debug.additions.find(R"("tags":["_logstash_parsed"])") !=
               std::string::npos);
  EXPECT_EQ(debug.time_formats.size(), 4) << "Deafult time formats missing";
  EXPECT_EQ(debug.escaping, utils::JsonRecordWriter::Escaping::EscapeAll);
  EXPECT_EQ(debug.input_format, pilorama::InputFormats::kTskv);

  const auto& release_input = configs[1].input;
  ASSERT_EQ(release_input.paths.size(), 2u);
  EXPECT_EQ(release_input.paths[0], "/test_path/release.log");
  EXPECT_EQ(release_input.paths[1], "/test_path/release.old.*.log");

  const pilorama::FilterConfig& release = configs[1].filter;
  EXPECT_EQ(release.timestamp_key, "unixtime");
  EXPECT_TRUE(release.transform_date);
  EXPECT_TRUE(release.drop_empty_fields);
  EXPECT_FALSE(release.put_message);
  EXPECT_EQ(release.minimal_log_level, pilorama::LogLevel::kWarning);
  EXPECT_EQ(release.removals.size(), 1u);
  EXPECT_TRUE(release.removals.count("metadata"));
  EXPECT_TRUE(release.renames.at("_type") == "type");
  EXPECT_TRUE(release.renames.at("_something") == "something_other");
  ASSERT_EQ(release.defaults.size(), 1);
  ASSERT_EQ(release.defaults.count("type"), 1);
  EXPECT_EQ(release.defaults.at("type"), "log");
  EXPECT_FALSE(release.additions.find("\"cgroups\":") != std::string::npos);
  EXPECT_TRUE(release.additions.find(R"("tags":["_logstash_parsed"])") !=
              std::string::npos);

  ASSERT_EQ(release.time_formats.size(), 1);
  EXPECT_EQ(release.time_formats.back(), "%Y-%m-%dT%H:%M:%S.%E*f");

  EXPECT_EQ(release.max_read_size, 100500);
  EXPECT_EQ(release.escaping,
            utils::JsonRecordWriter::Escaping::SimpleEscapeBypass);
  EXPECT_EQ(release.input_format, pilorama::InputFormats::kJson);
}

TEST(ConfigsLoading, FilterWithAnchor) {
  std::istringstream iss{R"(
    - file:
          path: "/test_path/debug.log"
          sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter: &debug
          transform_date: false
          drop_empty_fields: false
          put_message: true
          removals: ["metadata", "timestamp"]
          time_formats: ["%Y-%m-%dT%H:%M:%S.%E*f", "%Y-%m-%dT%H:%M:%S"]
          renames:
            - from: _type
              to: type
            - from: _something
              to: something_other
      output:
          hosts: localhost:9200
    - file:
          path: ["/test_path/release.log", "/test_path/release.old.*.log"]
          sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter: &release
          transform_date: true
          drop_empty_fields: true
          put_message: false
          removals: "metadata"
          additions:
            - '"tags":["_logstash_parsed"]'
            - '"hello":"word"'
          renames:
            - from: _type
              to: type
            - from: _something
              to: something_other
      output:
         hosts: localhost:9200

    - file:
          path: "/test_path/debug2.log"
          sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter: *debug
      output:
          hosts: localhost:9200
  )"};

  auto configs = pilorama::LoadConfigHelper(iss);
  ASSERT_EQ(configs.size(), 3u);

  const pilorama::FilterConfig& debug = configs[0].filter;
  EXPECT_FALSE(debug.transform_date);
  EXPECT_FALSE(debug.drop_empty_fields);
  EXPECT_TRUE(debug.put_message);
  EXPECT_EQ(debug.removals.size(), 2u);
  EXPECT_TRUE(debug.removals.count("metadata"));
  EXPECT_TRUE(debug.removals.count("timestamp"));
  EXPECT_TRUE(debug.renames.at("_type") == "type");
  EXPECT_TRUE(debug.renames.at("_something") == "something_other");
  EXPECT_FALSE(debug.additions.find("\"cgroups\":") != std::string::npos);
  EXPECT_FALSE(debug.additions.find(R"("tags":["_logstash_parsed"])") !=
               std::string::npos);
  EXPECT_EQ(debug.time_formats.size(), 2);

  const pilorama::FilterConfig& release = configs[1].filter;
  EXPECT_TRUE(release.transform_date);
  EXPECT_TRUE(release.drop_empty_fields);
  EXPECT_FALSE(release.put_message);
  EXPECT_EQ(release.removals.size(), 1u);
  EXPECT_TRUE(release.removals.count("metadata"));
  EXPECT_TRUE(release.renames.at("_type") == "type");
  EXPECT_TRUE(release.renames.at("_something") == "something_other");
  EXPECT_FALSE(release.additions.find("\"cgroups\":") != std::string::npos);
  EXPECT_TRUE(
      release.additions.find(R"("tags":["_logstash_parsed"],"hello":"word")") !=
      std::string::npos);

  const pilorama::FilterConfig& debug2 = configs[2].filter;
  EXPECT_EQ(debug.transform_date, debug2.transform_date);
  EXPECT_EQ(debug.drop_empty_fields, debug2.drop_empty_fields);
  EXPECT_EQ(debug.put_message, debug2.put_message);
  EXPECT_EQ(debug.removals.size(), debug2.removals.size());
  EXPECT_EQ(debug.additions, debug2.additions);
}

TEST(ConfigsLoading, FilterWithManyAnchors) {
  std::istringstream iss{R"(
    - file:
        path: &path_anchor ["/test_path/release.log", "/test_path/release.old.*.log"]
        sincedb_path: "/var/cache/logstash/fastcgi2-logs1.sincedb"
      filter: &debug
        transform_date: false
        drop_empty_fields: false
        put_message: true
        removals: ["metadata", "timestamp"]
        renames: &renames_anchor
          - from: _type
            to: type
          - from: _something
            to: something_other
      output: &out
        hosts: localhost:9200

    - file:
        path: *path_anchor
        sincedb_path: "/var/cache/logstash/fastcgi2-logs2.sincedb"
      filter: &release
        transform_date: true
        drop_empty_fields: true
        put_message: false
        removals: "metadata"
        additions: '"tags":["_logstash_parsed"]'
        renames: *renames_anchor
      output: *out
    - file:
        path: *path_anchor
        sincedb_path: "/var/cache/logstash/fastcgi2-logs3.sincedb"
      filter: *debug
      output: *out
    - file:
        path: *path_anchor
        sincedb_path: "/var/cache/logstash/fastcgi2-logs3.sincedb"
      filter: *debug
      output: *out
      )"};

  const std::vector<pilorama::ConfigEntry> configs =
      pilorama::LoadConfigHelper(iss);
  ASSERT_EQ(configs.size(), 4u);

  ASSERT_EQ(configs[0].input.paths.size(), 2u);
  ASSERT_EQ(configs[1].input.paths.size(), 2u);
  ASSERT_EQ(configs[2].input.paths.size(), 2u);
  ASSERT_EQ(configs[3].input.paths.size(), 2u);

  EXPECT_EQ(configs[0].input.paths, configs[1].input.paths);
  EXPECT_EQ(configs[0].input.paths, configs[2].input.paths);
  EXPECT_EQ(configs[0].input.paths, configs[3].input.paths);

  EXPECT_EQ(configs[0].filter.removals, configs[2].filter.removals);
  EXPECT_EQ(configs[0].filter.removals, configs[3].filter.removals);

  EXPECT_EQ(configs[0].filter.renames, configs[1].filter.renames);
  EXPECT_EQ(configs[0].filter.renames, configs[2].filter.renames);
  EXPECT_EQ(configs[0].filter.renames, configs[3].filter.renames);
}

TEST(ConfigsLoading, AnchorBeforeDefinition) {
  std::istringstream iss{R"(
      - file:
          path: &path_anchor ["/test_path/release.log", "/test_path/release.old.*.log"]
          sincedb_path: "/var/cache/logstash/fastcgi2-logs1.sincedb"
        filter: *release
        output:
          hosts: localhost:9200

      - file:
          path: *path_anchor
          sincedb_path: "/var/cache/logstash/fastcgi2-logs2.sincedb"
        filter: &release
          removals: ["metadata", "timestamp"]
        output:
          hosts: localhost:9200
        )"};

  EXPECT_ANY_THROW(pilorama::LoadConfigHelper(iss));
}

TEST(ConfigsLoading, Output) {
  std::istringstream iss{R"(
    - file:
        path: "/test_path/debug.log"
        sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter:
        transform_date: false
      output:
        index: "error-records"
        hosts: ["http://one.example", "http://two.example"]
        limit_all_retries: false
        balancing_group: some
        max_in_flight_requests: 2
        rate_limit: 20MiB/s
        elastic_version: 7
    - file:
        path: "/test_path/debug2.log"
        sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter:
        transform_date: false
      output:
        index: "doomed-records"
        error_index: "doomed-error-records"
        hosts: http://three.example
        send_timeout: 100
        max_retries: 100500
        initial_retry_delay: 1ms
        max_retry_delay: 1m
        limit_all_retries: true
        elastic_version: pre7
    )"};

  auto configs = pilorama::LoadConfigHelper(iss);
  ASSERT_EQ(configs.size(), 2u);

  const pilorama::OutputConfig& out0 = configs[0].output;
  EXPECT_EQ(out0.index, "error-records");
  ASSERT_EQ(out0.hosts.size(), 2u);
  EXPECT_EQ(out0.hosts[0], "http://one.example");
  EXPECT_EQ(out0.hosts[1], "http://two.example");
  EXPECT_EQ(out0.limit_all_retries, false);
  EXPECT_EQ(out0.balancing_group, "some");
  EXPECT_EQ(out0.max_in_flight_requests, 2);
  EXPECT_EQ(static_cast<long long>(out0.rate_limit), 20 * 1024 * 1024);
  EXPECT_EQ(out0.elastic_version, pilorama::ElasticVersion::Version7);

  const pilorama::OutputConfig& out1 = configs[1].output;
  EXPECT_EQ(out1.index, "doomed-records");
  EXPECT_EQ(out1.error_index, "doomed-error-records");
  ASSERT_EQ(out1.hosts.size(), 1u);
  EXPECT_EQ(out1.hosts[0], "http://three.example");

  EXPECT_EQ(out1.send_timeout, std::chrono::seconds(100));
  EXPECT_EQ(out1.max_retries, 100500);

  EXPECT_EQ(out1.initial_retry_delay, std::chrono::milliseconds(1));
  EXPECT_EQ(out1.max_retry_delay, std::chrono::minutes(1));
  EXPECT_EQ(out1.limit_all_retries, true);
  EXPECT_EQ(out1.balancing_group, "");
  EXPECT_EQ(out1.max_in_flight_requests, 0);
  EXPECT_EQ(static_cast<long long>(out1.rate_limit), 0);
  EXPECT_EQ(out1.elastic_version, pilorama::ElasticVersion::VersionPre7);
}

TEST(ConfigsLoading, FilterCgroups) {
  std::istringstream iss{R"(
      - file:
          path: "/test_path/debug.log"
          sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
        filter:
          cgroups: true
          cgroups_to_ignore: "" # Empty
        output:
          hosts: localhost:9200
      )"};

  try {
    auto configs = pilorama::LoadConfigHelper(iss);
    ASSERT_EQ(configs.size(), 1u);
    EXPECT_TRUE(configs[0].filter.additions.find("\"cgroups\":") !=
                std::string::npos);
  } catch (const std::exception& e) {
    const std::string msg{e.what()};
    EXPECT_TRUE(msg.find("Failed to open file") != std::string::npos ||
                msg.find("Error during search and parse of") !=
                    std::string::npos)
        << "Message was: " << msg;
  }
}

TEST(ConfigsLoading, FilterFromEnv) {
  std::istringstream iss{R"(
        - file:
            path: "/test_path/debug.log"
            sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
          filter:
            add_from_env:
            - from: PILORAMA_TEST_VARIABLE_1
              to: pilorama_test_variable_1_key
            - from: PILORAMA_TEST_VARIABLE_2
              to: pilorama_test_variable_2_key
            - from: PILORAMA_TEST_VARIABLE_3
              to: pilorama_test_variable_3_key
          output:
            hosts: localhost:9200
    )"};

  setenv("PILORAMA_TEST_VARIABLE_1", "pilorama_test_variable_1_value", 0);
  setenv("PILORAMA_TEST_VARIABLE_2", "pilorama_test_variable_\"2\"_value", 0);

  auto configs = pilorama::LoadConfigHelper(iss);
  ASSERT_EQ(configs.size(), 1u);
  const auto& additions = configs[0].filter.additions;

  EXPECT_NE(additions.find("\"pilorama_test_variable_1_key\":\"pilorama_test_"
                           "variable_1_value\""),
            std::string::npos);

  EXPECT_NE(additions.find("\"pilorama_test_variable_2_key\":\"pilorama_test_"
                           "variable_\\\"2\\\"_value\""),
            std::string::npos);

  EXPECT_NE(additions.find("\"pilorama_test_variable_3_key\":\"\""),
            std::string::npos);

  EXPECT_NE(
      additions.find(
          "\"pilorama_test_variable_1_key\":\"pilorama_test_variable_1_value\","
          "\"pilorama_test_variable_2_key\":\"pilorama_test_variable_\\\"2\\\"_"
          "value\",\"pilorama_test_variable_3_key\":\"\""),
      std::string::npos)
      << "Additions == " << additions;
}

class ConfigsFileLoading : public ::testing::TestWithParam<TestnameFilename> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, ConfigsFileLoading,
    ::testing::ValuesIn(TestnameFilenameData{
        {"sample", "pilorama_config.sample.yaml"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(ConfigsFileLoading, Samples) {
  boost::filesystem::path path = __FILE__;
  path = path.parent_path();
  path = path / ".." / "configs" / "samples" / GetParam().filename;
  std::ifstream ifs{};

  ASSERT_NO_THROW(ifs.open(path.c_str())) << "Failed to open " << path.string();

  std::vector<pilorama::ConfigEntry> configs;
  configs = pilorama::LoadConfigHelper(ifs);
  EXPECT_EQ(configs.size(), 3) << "Failed to load from " << path.string();
}

TEST(JaegerConfigsFileLoading, JaegerSample) {
  boost::filesystem::path path = __FILE__;
  path = path.parent_path();
  path = path / ".." / "configs" / "samples" / "pilorama_config_jaeger.yaml";
  std::ifstream ifs{};

  ASSERT_NO_THROW(ifs.open(path.c_str())) << "Failed to open " << path.string();

  std::vector<pilorama::ConfigEntry> configs;
  configs = pilorama::LoadConfigHelper(ifs);
  EXPECT_EQ(configs.size(), 2) << "Failed to load from " << path.string();
}

////////////////////////////////////////////////////////////////////////////////

class ConfigsLoadingException
    : public ::testing::TestWithParam<ExceptionCheck> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, ConfigsLoadingException,
    ::testing::ValuesIn(ExceptionCheckData{
        {"date_is_not_a_bool", "[0]->filter->transform_date",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  filter: &debug
    transform_date: "not a bool"
)"},

        {"no_syncdb_path", "[1]->file->sincedb_path",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  output:
    hosts: localhost:9200
- file:
    path: "/test_path/debug.log"
)"},

        {"uncosumed_data", "unconsumed data",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
    pth: "/test_path/debug.log"
  output:
    hosts: localhost:9200
)"},

        {"date_is_not_a_bool_again", "[1]->filter->transform_date",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  output:
    hosts: localhost:9200
- file:
    path: ["/test_path/release.log", "/test_path/release.old.*.log"]
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  filter: &release
    transform_date: "not a bool"
    drop_empty_fields: true
  output:
    hosts: localhost:9200
)"},

        {"time_formats_is_an_array_of_maps", "[0]->filter->time_formats",
         R"(
 - file:
     path: ["/test_path/release.log", "/test_path/release.old.*.log"]
     sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
   filter: &release
     time_formats:
          - one: 1
          - two: 2
     drop_empty_fields: true
   output:
     hosts: localhost:9200
 )"},

        {"time_formats_is_a_map", "[0]->filter->time_formats",
         R"(
 - file:
     path: ["/test_path/release.log", "/test_path/release.old.*.log"]
     sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
   filter: &release
     time_formats:
          one: 1
          two: 2
     drop_empty_fields: true
   output:
     hosts: localhost:9200
 )"},

        {"time_formats_is_empty", "[0]->filter->time_formats",
         R"(
  - file:
      path: ["/test_path/release.log", "/test_path/release.old.*.log"]
      sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
    filter: &release
      time_formats:
      drop_empty_fields: true
    output:
      hosts: localhost:9200
  )"},

        {"timestamp_is_empty", "'[0]->filter->timestamp_key'",
         R"(
   - file:
       path: ["/test_path/release.log", "/test_path/release.old.*.log"]
       sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
     filter: &release
       timestamp_key:
       drop_empty_fields: true
     output:
       hosts: localhost:9200
   )"},

        {"escaping_is_wrong", "[0]->filter->escaping",
         R"(
  - file:
      path: ["/test_path/release.log", "/test_path/release.old.*.log"]
      sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
    filter: &release
      escaping: incorrect
      drop_empty_fields: true
    output:
      hosts: localhost:9200
  )"},

        {"cgroups_is_not_a_bool", "[1]->filter->cgroups",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  output: &out
    hosts: localhost:9200
- file:
    path: ["/test_path/release.log", "/test_path/release.old.*.log"]
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  filter: &release
    removals: "metadata"
    cgroups: "not a bool"
    additions: '"tags":["_logstash_parsed"]'
  output: *out
)"},

        {"no_syncdb_path_second_entry", "[1]->file->sincedb_path",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  output: &out
    hosts: localhost:9200
- file:
    path: ["/test_path/release.log", "/test_path/release.old.*.log"]
  output: *out
)"},

        {"initial_retry_dealy_is_zero", "initial_retry_delay",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  filter:
  output:
     hosts: localhost:9200
     initial_retry_delay: 0s
 )"},

        {"max_retry_dealy_greater_than_initial", "max_retry_delay",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  filter:
  output:
    hosts: localhost:9200
    initial_retry_delay: 2s
    max_retry_delay: 1s
  )"},

        {"limit_all_retries_is_float", "limit_all_retries",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  filter:
  output:
    hosts: localhost:9200
    initial_retry_delay: 2s
    limit_all_retries: 1.1
  )"},

        {"too_small_read_size", "max_read_size",
         R"(
 - file:
     path: "/test_path/debug.log"
     sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
   filter: &debug
     max_read_size: 100
 )"},

        {"unknown_log_level", "PAPAPIDUP",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  filter: &debug
    minimal_log_level: PAPAPIDUP
)"},

        {"balancing_groups_no_max_in_flight",
         "has a `balancing_group` but no explicitly specified "
         "`max_in_flight_request`",
         R"(
- file:
    path: "/test_path/debug.log"
    sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
  output:
    hosts: localhost:9200
    balancing_group: default
)"},

        {"unknown_elastic_version", "ElasticVersion",
         R"(
 - file:
     path: "/test_path/debug.log"
     sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
   output:
     hosts: localhost:9200
     elastic_version: BAD
 )"},

        {"bad_input_format", "binary coded decimals",
         R"(
  - file:
      path: "/test_path/debug.log"
      sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
    output:
      hosts: localhost:9200
      input_format: binary coded decimals
  )"},

        {"balancing_groups_missmatch",
         "have different `max_in_flight_requests`",
         R"(
 - file:
     path: "/test_path/debug.log"
     sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
   output:
     hosts: localhost:9200
     max_in_flight_requests: 7
     balancing_group: default
 - file:
     sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
     path: ["/test_path/release.log", "/test_path/release.old.*.log"]
   output:
     hosts: [localhost:9200,localhost:9201]
     max_in_flight_requests: 42
     balancing_group: default
 )"},
    }),
    ::testing::PrintToStringParamName());

TEST_P(ConfigsLoadingException, Errors) {
  const auto d = GetParam();
  std::istringstream iss{d.config};
  bool catched_exception = false;
  try {
    pilorama::LoadConfigHelper(iss);
  } catch (const std::exception& e) {
    catched_exception = true;
    std::string error_msg{e.what()};
    EXPECT_NE(error_msg.find(d.message), std::string::npos)
        << "failed to find '" << d.message << "' in '" << error_msg << "'";
  }
  EXPECT_TRUE(catched_exception);
}

TEST(ConfigsLoading, CorrectJaegerFormat) {
  std::istringstream iss{R"(
    - file:
       path: "/test_path/debug.log"
       sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter:
      output:
       hosts: localhost:9200
    - file:
       path: "/test_path/opentracing.log"
       sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter:
       input_format: tskv-jaeger-span
      output:
       jaeger_service_index: jaeger-service-index
       hosts: localhost:9200
    - file:
       path: "/test_path/opentracing.log"
       sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter:
       input_format: tskv-jaeger-span
      output:
       format: jaeger-collector
       hosts: localhost:9200
    )"};

  auto configs = pilorama::LoadConfigHelper(iss);
  ASSERT_EQ(configs.size(), 3u);

  EXPECT_TRUE(configs[0].output.jaeger_service_index.empty());

  EXPECT_EQ(configs[1].output.jaeger_service_index, "jaeger-service-index");
  EXPECT_EQ(configs[1].filter.input_format,
            pilorama::InputFormats::kTskvJaegerSpan);

  EXPECT_EQ(configs[1].output.format, pilorama::OutputFormat::kElastic);

  EXPECT_EQ(configs[2].output.format, pilorama::OutputFormat::kJaegerCollector);
}

TEST(ConfigsLoading, JaegerServiceindexNotSet) {
  std::istringstream iss{R"(
    - file:
       path: "/test_path/opentracing.log"
       sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter:
       input_format: tskv-jaeger-span
      output:
       hosts: localhost:9200
    )"};

  EXPECT_ANY_THROW(pilorama::LoadConfigHelper(iss));
}

TEST(ConfigsLoading, JaegerInputFormatNotSet) {
  std::istringstream iss{R"(
    - file:
       path: "/test_path/opentracing.log"
       sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter:
       input_format: tskv
      output:
       jaeger_service_index: jaeger-service-index
       hosts: localhost:9200
    )"};

  EXPECT_ANY_THROW(pilorama::LoadConfigHelper(iss));
}

TEST(ConfigsLoading, RenameNotJaegerField) {
  std::istringstream iss{R"(
    - file:
       path: "/test_path/opentracing.log"
       sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
      filter:
       renames:
         - from: not_jaeger_key
           to: test
       input_format: tskv-jaeger-span
      output:
       jaeger_service_index: jaeger-service-index
       hosts: localhost:9200
    )"};

  EXPECT_ANY_THROW(pilorama::LoadConfigHelper(iss));
}

TEST(ConfigsLoading, CustomConfigs) {
  const fs::blocking::TempFile config_file = fs::blocking::TempFile::Create();
  const fs::blocking::TempDirectory custom_config_dir =
      fs::blocking::TempDirectory::Create();
  const fs::blocking::TempFile custom_config_file =
      fs::blocking::TempFile::Create(custom_config_dir.GetPath(), "");

  {
    std::ofstream default_ofs{config_file.GetPath().c_str()};
    if (default_ofs.fail()) {
      throw std::runtime_error("Failed to open for writing config file " +
                               config_file.GetPath());
    }
    default_ofs << R"(
      - file:
         path: "/test_path/debug.log"
         sincedb_path: "/var/cache/logstash/fastcgi2-logs.sincedb"
        filter:
        output:
         hosts: localhost:9200
    )";

    std::ofstream custom_ofs{custom_config_file.GetPath().c_str()};
    if (custom_ofs.fail()) {
      throw std::runtime_error("Failed to open for writing config file " +
                               custom_config_file.GetPath());
    }
    custom_ofs << R"(
      - file:
         path: "/some/other/path.log"
         sincedb_path: "/var/cache/logstash/some-other-path.sincedb"
        filter:
        output:
         hosts: localhost:9200
    )";
  }

  auto configs_entries = pilorama::GetRulesFromFs(config_file.GetPath(),
                                                  custom_config_dir.GetPath());

  EXPECT_EQ(configs_entries.size(), 2);
  EXPECT_EQ(configs_entries[0].input.exclude_paths.size(), 0);
  EXPECT_EQ(configs_entries[1].input.exclude_paths.size(), 1);
  EXPECT_EQ(configs_entries[1].input.exclude_paths.back(),
            "/some/other/path.log");
}
