#include "elastic/batch_process.hpp"

#include <cstring>

#include <gtest/gtest.h>

#include <userver/utils/mock_now.hpp>

namespace {

using pilorama::elastic::BatchProcess;
using pilorama::elastic::LimitingStreamPolicyFactory;

namespace produce_150_bytes {

///// Parent 2

constexpr std::string_view kJsonLink01Parent02 =
    R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"log"}})"
    "\n"
    R"({"text":"record 01 @@ 02","link":"01","parent_link":"02","level":"INFO"})"
    "\n";
constexpr std::string_view kTskvLink01Parent02 =
    "tskv\ttext=record 01 @@ 02\tlink=01\tparent_link=02\tlevel=INFO\n";

constexpr std::string_view kJsonLink03Parent02 =
    R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"log"}})"
    "\n"
    R"({"text":"record 03 @@ 02","link":"03","parent_link":"02","level":"INFO"})"
    "\n";
constexpr std::string_view kTskvLink03Parent02 =
    "tskv\ttext=record 03 @@ 02\tlink=03\tparent_link=02\tlevel=INFO\n";

constexpr std::string_view kJsonLink04ErrorParent02 =
    R"({"index":{"_index":"ERRORR_INDEX","_id":null,"_routing":null,"_type":"log"}})"
    "\n"
    R"({"text":"recrd 04 @@ 02","link":"04","parent_link":"02","level":"ERROR"})"
    "\n";
constexpr std::string_view kJsonLink04Parent02 =
    R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"log"}})"
    "\n"
    R"({"text":"recrd 04 @@ 02","link":"04","parent_link":"02","level":"ERROR"})"
    "\n";
constexpr std::string_view kTskvLink04ErrorParent02 =
    "tskv\ttext=recrd 04 @@ 02\tlink=04\tparent_link=02\tlevel=ERROR\n";

///// Parent 10

constexpr std::string_view kJsonLink05Parent10 =
    R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"log"}})"
    "\n"
    R"({"text":"record 05 @@ 10","link":"05","parent_link":"10","level":"INFO"})"
    "\n";
constexpr std::string_view kTskvLink05Parent10 =
    "tskv\ttext=record 05 @@ 10\tlink=05\tparent_link=10\tlevel=INFO\n";

constexpr std::string_view kJsonLink06Parent10 =
    R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"log"}})"
    "\n"
    R"({"text":"record 06 @@ 10","link":"06","parent_link":"10","level":"INFO"})"
    "\n";
constexpr std::string_view kTskvLink06Parent10 =
    "tskv\ttext=record 06 @@ 10\tlink=06\tparent_link=10\tlevel=INFO\n";

///// No Link + Parent2

constexpr std::string_view kJsonNoLinkParent02 =
    R"({"index":{"_index":"COMMON_INDEX","_id":null,"_routing":null,"_type":"log"}})"
    "\n"
    R"({"text":"record no link at all @@ 02","parent_link":"02","level":"INFO"})"
    "\n";
constexpr std::string_view kTskvNoLinkParent02 =
    "tskv\ttext=record no link at all @@ 02\tparent_link=02\tlevel=INFO\n";

}  // namespace produce_150_bytes

template <class... Args>
std::string ConcantenateViews(Args... views) {
  std::string result;
  result.reserve((views.size() + ...));
  (result.append(views), ...);
  return result;
}

}  // namespace

TEST(BatchProcessLimiting, LimitNotHit) {
  utils::datetime::MockNowSet({});

  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  output_config.index = "COMMON_INDEX";
  output_config.error_index = "ERROR_INDEX";

  pilorama::StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{700});
  limiter.SetWindowSize(10);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  auto tskv = ConcantenateViews(produce_150_bytes::kTskvLink01Parent02,
                                produce_150_bytes::kTskvLink03Parent02,
                                produce_150_bytes::kTskvLink05Parent10,
                                produce_150_bytes::kTskvLink06Parent10);

  const auto batch = BatchProcess(f, output_config, tskv,
                                  LimitingStreamPolicyFactory(limiter));
  for (auto value : {
           produce_150_bytes::kJsonLink01Parent02,
           produce_150_bytes::kJsonLink03Parent02,
           produce_150_bytes::kJsonLink05Parent10,
           produce_150_bytes::kJsonLink06Parent10,
       }) {
    EXPECT_NE(batch.full.find(value), std::string::npos)
        << "Failed to find '" << value << "' in '" << batch.full << "'";
  }
  EXPECT_EQ(batch.stats.input_bytes_processed, tskv.size());
  EXPECT_EQ(batch.full.size(), 600);
  EXPECT_TRUE(batch.error.empty());
}

TEST(BatchProcessLimiting, LimitIsHit) {
  utils::datetime::MockNowSet({});

  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  output_config.index = "COMMON_INDEX";
  output_config.error_index = "ERROR_INDEX";

  pilorama::StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{450});
  limiter.SetWindowSize(10);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // For new link ids: recent ids are preferred over older ones
  {
    auto tskv = ConcantenateViews(produce_150_bytes::kTskvLink01Parent02,
                                  produce_150_bytes::kTskvLink03Parent02,
                                  produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10);

    const auto batch = BatchProcess(f, output_config, tskv,
                                    LimitingStreamPolicyFactory(limiter));

    for (auto value : {
             produce_150_bytes::kJsonLink05Parent10,
             produce_150_bytes::kJsonLink06Parent10,
         }) {
      EXPECT_NE(batch.full.find(value), std::string::npos)
          << "Failed to find '" << value << "' in '" << batch.full << "'";
    }
    EXPECT_EQ(batch.stats.input_bytes_processed, tskv.size());
    EXPECT_EQ(batch.full.size(), 300);
    EXPECT_TRUE(batch.error.empty());
  }

  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // On overflow at least some of the old logs are written
  {
    auto tskv = ConcantenateViews(produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink06Parent10);

    const auto batch = BatchProcess(f, output_config, tskv,
                                    LimitingStreamPolicyFactory(limiter));
    EXPECT_EQ(batch.stats.input_bytes_processed, tskv.size());
    EXPECT_EQ(batch.full.size(), 450);
    EXPECT_TRUE(batch.error.empty());
  }

  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // Once logged links are preferred
  {
    auto tskv = ConcantenateViews(produce_150_bytes::kTskvLink01Parent02,
                                  produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink03Parent02);

    const auto batch = BatchProcess(f, output_config, tskv,
                                    LimitingStreamPolicyFactory(limiter));
    for (auto value : {
             produce_150_bytes::kJsonLink05Parent10,
             produce_150_bytes::kJsonLink06Parent10,
             produce_150_bytes::kJsonLink06Parent10,
         }) {
      EXPECT_NE(batch.full.find(value), std::string::npos)
          << "Failed to find '" << value << "' in '" << batch.full << "'";
    }
    EXPECT_EQ(batch.stats.input_bytes_processed, tskv.size());
    EXPECT_EQ(batch.full.size(), 450);
    EXPECT_TRUE(batch.error.empty());
  }

  // Testing SetMaxSize increase
  limiter.SetMaxOutputSize(utils::BytesPerSecond{900});
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});
  {
    auto tskv = ConcantenateViews(produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink06Parent10);

    const auto batch = BatchProcess(f, output_config, tskv,
                                    LimitingStreamPolicyFactory(limiter));
    EXPECT_EQ(batch.stats.input_bytes_processed, tskv.size());
    EXPECT_EQ(batch.full.size(), 900);
    EXPECT_TRUE(batch.error.empty());
  }

  // Testing SetMaxSize decrease
  limiter.SetMaxOutputSize(utils::BytesPerSecond{200});
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});
  {
    auto tskv = ConcantenateViews(produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10,
                                  produce_150_bytes::kTskvLink06Parent10);

    const auto batch = BatchProcess(f, output_config, tskv,
                                    LimitingStreamPolicyFactory(limiter));
    EXPECT_EQ(batch.stats.input_bytes_processed, tskv.size());
    EXPECT_EQ(batch.full.size(), 150);
    EXPECT_TRUE(batch.error.empty());
  }
}

TEST(BatchProcessLimiting, LimitIsHitErrorIndex) {
  utils::datetime::MockNowSet({});

  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  output_config.index = "COMMON_INDEX";
  output_config.error_index = "ERRORR_INDEX";

  pilorama::StreamLimiter limiter;
  limiter.SetWindowSize(10);
  limiter.SetMaxOutputSize(utils::BytesPerSecond{450});
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  {
    auto tskv = ConcantenateViews(produce_150_bytes::kTskvLink01Parent02,
                                  produce_150_bytes::kTskvLink04ErrorParent02,
                                  produce_150_bytes::kTskvLink03Parent02,
                                  produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10);

    const auto batch = BatchProcess(f, output_config, tskv,
                                    LimitingStreamPolicyFactory(limiter));

    for (auto value : {
             produce_150_bytes::kJsonLink01Parent02,
             produce_150_bytes::kJsonLink03Parent02,
             produce_150_bytes::kJsonLink04Parent02,
         }) {
      EXPECT_NE(batch.full.find(value), std::string::npos)
          << "Failed to find '" << value << "' in '" << batch.full << "'";
    }
    EXPECT_EQ(batch.stats.input_bytes_processed, tskv.size());
    EXPECT_EQ(batch.full.size(), 450);
    EXPECT_EQ(batch.error, produce_150_bytes::kJsonLink04ErrorParent02);
  }
}

TEST(BatchProcessLimiting, LimitIsHitNoLink) {
  utils::datetime::MockNowSet({});

  pilorama::OutputConfig output_config{};
  pilorama::FilterConfig f;
  f.put_message = false;
  output_config.index = "COMMON_INDEX";
  output_config.error_index = "ERRORR_INDEX";

  pilorama::StreamLimiter limiter;
  limiter.SetWindowSize(15);
  limiter.SetMaxOutputSize(utils::BytesPerSecond{650});
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  {
    auto tskv = ConcantenateViews(produce_150_bytes::kTskvNoLinkParent02,
                                  produce_150_bytes::kTskvLink01Parent02,
                                  produce_150_bytes::kTskvLink04ErrorParent02,
                                  produce_150_bytes::kTskvLink05Parent10,
                                  produce_150_bytes::kTskvLink06Parent10);

    const auto batch = BatchProcess(f, output_config, tskv,
                                    LimitingStreamPolicyFactory(limiter));

    for (auto value : {
             produce_150_bytes::kJsonLink01Parent02,
             produce_150_bytes::kJsonNoLinkParent02,  // in batch due to parent
             produce_150_bytes::kJsonLink04Parent02,
         }) {
      EXPECT_NE(batch.full.find(value), std::string::npos)
          << "Failed to find '" << value << "' in '" << batch.full << "'";
    }
    EXPECT_EQ(batch.stats.input_bytes_processed, tskv.size());
    EXPECT_EQ(batch.full.size(), 450);
    EXPECT_EQ(batch.error, produce_150_bytes::kJsonLink04ErrorParent02);
  }
}
