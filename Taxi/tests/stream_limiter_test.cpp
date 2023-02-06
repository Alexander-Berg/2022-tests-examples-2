#include <stream_limiter.hpp>

#include <algorithm>
#include <array>
#include <vector>

#include <gtest/gtest.h>

#include <userver/utils/mock_now.hpp>

namespace {
constexpr std::size_t kTotalRecords = 6;

constexpr std::string_view kRecords10Bytes[kTotalRecords] = {
    {"record #01", 10}, {"record #02", 10}, {"record #03", 10},
    {"record #04", 10}, {"record #05", 10}, {"record #06", 10},
};

constexpr utils::BytesPerSecond kUnlimited{
    std::numeric_limits<long long>::max()};
constexpr auto kWindowSize = 1000;

using StreamLimiter = pilorama::StreamLimiter;
using Link = pilorama::HashedLink;

enum class TestModes {
  kNoLink,
  kNoLinkError,
  kLink,
  kLinkError,
  kLinkAndParentAsc,
  kLinkErrorAndParentAsc,
  kLinkAndParentDesc,
  kLinkErrorAndParentDesc,
  kLinkAndParentUnrelated,
  kLinkErrorAndParentUnrelated,
};
inline std::string PrintToString(TestModes mode) {
  switch (mode) {
    case TestModes::kNoLink:
      return "NoLink";
    case TestModes::kNoLinkError:
      return "NoLinkError";
    case TestModes::kLink:
      return "Link";
    case TestModes::kLinkError:
      return "LinkError";
    case TestModes::kLinkAndParentAsc:
      return "kLinkAndParentAsc";
    case TestModes::kLinkErrorAndParentAsc:
      return "kLinkErrorAndParentAsc";
    case TestModes::kLinkAndParentDesc:
      return "kLinkAndParentDesc";
    case TestModes::kLinkErrorAndParentDesc:
      return "kLinkErrorAndParentDesc";
    case TestModes::kLinkAndParentUnrelated:
      return "kLinkAndParentUnrelated";
    case TestModes::kLinkErrorAndParentUnrelated:
      return "kLinkErrorAndParentUnrelated";
  }
}

void BasicTestLimiter(StreamLimiter& limiter, TestModes mode,
                      std::size_t index) {
  switch (mode) {
    case TestModes::kNoLink:
      limiter.HandleNoLinkRecord();
      break;
    case TestModes::kNoLinkError:
      limiter.HandleNoLinkErrorRecord();
      break;
    case TestModes::kLink:
      limiter.SetLink(Link{index});
      limiter.HandleRecord();
      break;
    case TestModes::kLinkError:
      limiter.SetLink(Link{index});
      limiter.OnImportantRecord();
      limiter.HandleRecord();
      break;
    case TestModes::kLinkAndParentAsc:
      limiter.SetLink(Link{index});
      limiter.OnParent(Link{index - 1});
      limiter.HandleRecord();
      break;
    case TestModes::kLinkErrorAndParentAsc:
      limiter.SetLink(Link{index});
      limiter.OnParent(Link{kTotalRecords - index});
      limiter.OnImportantRecord();
      limiter.HandleRecord();
      break;
    case TestModes::kLinkAndParentDesc:
      limiter.SetLink(Link{index});
      limiter.OnParent(Link{kTotalRecords - index});
      limiter.HandleRecord();
      break;
    case TestModes::kLinkErrorAndParentDesc:
      limiter.SetLink(Link{index});
      limiter.OnParent(Link{kTotalRecords - index});
      limiter.OnImportantRecord();
      limiter.HandleRecord();
      break;
    case TestModes::kLinkAndParentUnrelated:
      limiter.SetLink(Link{index});
      limiter.OnParent(Link{kTotalRecords + 1 + kTotalRecords * index});
      limiter.HandleRecord();
      break;
    case TestModes::kLinkErrorAndParentUnrelated:
      limiter.SetLink(Link{index});
      limiter.OnParent(Link{kTotalRecords + 1 + kTotalRecords * index});
      limiter.OnImportantRecord();
      limiter.HandleRecord();
      break;
  }
}

}  // namespace

////////////////////////////////////////////////////////////////////////////////
/// Basic tests to log all or log nothing
class StreamLimiterBasic : public ::testing::TestWithParam<TestModes> {};

INSTANTIATE_TEST_SUITE_P(
    /*no prefix*/, StreamLimiterBasic,
    ::testing::ValuesIn({
        TestModes::kNoLink,
        TestModes::kNoLinkError,
        TestModes::kLink,
        TestModes::kLinkError,
        TestModes::kLinkAndParentAsc,
        TestModes::kLinkErrorAndParentAsc,
        TestModes::kLinkAndParentDesc,
        TestModes::kLinkErrorAndParentDesc,
        TestModes::kLinkAndParentUnrelated,
        TestModes::kLinkErrorAndParentUnrelated,
    }),
    ::testing::PrintToStringParamName());

TEST_P(StreamLimiterBasic, LogAll) {
  utils::datetime::MockNowSet({});

  const auto param = GetParam();
  StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{kUnlimited});
  limiter.SetWindowSize(kWindowSize);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  for (size_t i = 0; i < kTotalRecords; ++i) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    BasicTestLimiter(limiter, param, i);
  }
  const auto result = limiter.EndChunkAndGetRecordsBatch();

  for (size_t i = 0; i < kTotalRecords; ++i) {
    EXPECT_NE(result.find(kRecords10Bytes[i]), std::string::npos)
        << "'" << kRecords10Bytes[i] << "' not in '" << result << "'";
  }

  EXPECT_EQ(result.size(), kRecords10Bytes[0].size() * kTotalRecords);
}

TEST_P(StreamLimiterBasic, LogAllReuse) {
  utils::datetime::MockNowSet({});

  const auto param = GetParam();
  StreamLimiter limiter;
  limiter.SetMaxOutputSize(kUnlimited);
  limiter.SetWindowSize(kWindowSize);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  auto halfRange = kTotalRecords / 2;

  std::string results[2];
  for (size_t j = 0; j < 2; ++j) {
    for (size_t i = halfRange * j; i < halfRange * (j + 1); ++i) {
      limiter.NewRecord(std::string(kRecords10Bytes[i]));
      BasicTestLimiter(limiter, param, i);
    }
    results[j] = limiter.EndChunkAndGetRecordsBatch();

    for (size_t i = halfRange * j; i < halfRange * (j + 1); ++i) {
      EXPECT_NE(results[j].find(kRecords10Bytes[i]), std::string::npos)
          << "'" << kRecords10Bytes[i] << "' not in '" << results[j] << "'";
    }
  }

  EXPECT_NE(results[0], results[1]) << "Something is wrong with test";
  EXPECT_EQ(results[0].size(), kRecords10Bytes[0].size() * halfRange);
  EXPECT_EQ(results[0].size(), results[1].size())
      << "Something is wrong with test";
}

TEST_P(StreamLimiterBasic, LogNone) {
  utils::datetime::MockNowSet({});

  const auto param = GetParam();
  StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{9});
  limiter.SetWindowSize(kWindowSize);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  for (size_t i = 0; i < kTotalRecords; ++i) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    BasicTestLimiter(limiter, param, i);
  }
  const auto result = limiter.EndChunkAndGetRecordsBatch();
  EXPECT_TRUE(result.empty()) << "Result = " << result;
}

TEST_P(StreamLimiterBasic, LogNoneReuse) {
  utils::datetime::MockNowSet({});

  const auto param = GetParam();
  StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{9});
  limiter.SetWindowSize(kWindowSize);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  auto halfRange = kTotalRecords / 2;

  for (size_t j = 0; j < 2; ++j) {
    for (size_t i = halfRange * j; i < halfRange * (j + 1); ++i) {
      limiter.NewRecord(std::string(kRecords10Bytes[i]));
      BasicTestLimiter(limiter, param, i);
    }
    const auto result = limiter.EndChunkAndGetRecordsBatch();
    EXPECT_TRUE(result.empty()) << "Result = " << result;
  }
}

TEST_P(StreamLimiterBasic, Smoothing) {
  utils::datetime::MockNowSet({});

  const auto param = GetParam();
  StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{10});
  limiter.SetWindowSize(kWindowSize);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  {
    limiter.NewRecord(std::string(kRecords10Bytes[0]));
    BasicTestLimiter(limiter, param, 0);
    const auto result = limiter.EndChunkAndGetRecordsBatch();
    EXPECT_EQ(result.size(), 10) << "Result = " << result;
  }

  utils::datetime::MockSleep(std::chrono::seconds{5});

  {
    for (size_t i = 0; i < kTotalRecords; ++i) {
      limiter.NewRecord(std::string(kRecords10Bytes[i]));
      BasicTestLimiter(limiter, param, i);
    }
    const auto result = limiter.EndChunkAndGetRecordsBatch();
    EXPECT_GE(result.size(), 20) << "Result = " << result;
  }
}

////////////////////////////////////////////////////////////////////////////////
/// Tests to separate pools of links and log only one of them

TEST(StreamLimiterGroups, LogGroupsNoParent) {
  utils::datetime::MockNowSet({});

  StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{30});
  limiter.SetWindowSize(kWindowSize);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  auto halfRange = kTotalRecords / 2;

  // Make sure that we prefer the second group, because chances are high that
  // it will appear in next chunk

  for (size_t j = 0; j < 2; ++j) {
    for (size_t i = halfRange * j; i < halfRange * (j + 1); ++i) {
      limiter.NewRecord(std::string(kRecords10Bytes[i]));
      limiter.SetLink(Link{j});
      limiter.HandleRecord();
    }
  }
  {
    const auto result1 = limiter.EndChunkAndGetRecordsBatch();
    for (size_t i = halfRange; i < kTotalRecords; ++i) {
      EXPECT_NE(result1.find(kRecords10Bytes[i]), std::string::npos)
          << "'" << kRecords10Bytes[i] << "' not in '" << result1 << "'";
    }
  }

  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // Make sure that the group is remembered between `EndChunkAndGetResult` calls

  for (size_t j = 0; j < 2; ++j) {
    for (size_t i = halfRange * j; i < halfRange * (j + 1); ++i) {
      limiter.NewRecord(std::string(kRecords10Bytes[i]));
      limiter.SetLink(Link{1 - j});
      limiter.HandleRecord();
    }
  }
  {
    const auto result2 = limiter.EndChunkAndGetRecordsBatch();
    for (size_t i = 0; i < halfRange; ++i) {
      EXPECT_NE(result2.find(kRecords10Bytes[i]), std::string::npos)
          << "'" << kRecords10Bytes[i] << "' not in '" << result2 << "'";
    }
  }

  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // Make sure that old group is remembered to ignore between
  // `EndChunkAndGetResult` calls

  for (auto i : {
           2u,  // new group
           1u,  // group already logged
           0u,  // group already ignored
       }) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{i});
    limiter.HandleRecord();
  }
  {
    const auto result3 = limiter.EndChunkAndGetRecordsBatch();
    EXPECT_NE(result3.find(kRecords10Bytes[2]), std::string::npos)
        << "'" << kRecords10Bytes[2] << "' not in '" << result3 << "'";
    EXPECT_NE(result3.find(kRecords10Bytes[1]), std::string::npos)
        << "'" << kRecords10Bytes[1] << "' not in '" << result3 << "'";

    EXPECT_EQ(result3.find(kRecords10Bytes[0]), std::string::npos)
        << "'" << kRecords10Bytes[0] << "' not in '" << result3 << "'";

    EXPECT_EQ(result3.size(), 20);
  }

  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // Make sure that new group with error is preferred over other groups and that
  // groups are remembered between `EndChunkAndGetResult` calls

  for (auto i : {
           5u,  // new group
           4u,  // new group with error
           3u,  // new group
           2u,  // group already logged
           1u,  // group already logged
           0u,  // group already ignored
       }) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{i});
    if (i == 4) {
      limiter.OnImportantRecord();
    }
    limiter.HandleRecord();
  }
  {
    const auto result = limiter.EndChunkAndGetRecordsBatch();
    for (auto i : {2, 1, 4}) {
      EXPECT_NE(result.find(kRecords10Bytes[i]), std::string::npos)
          << "'" << kRecords10Bytes[i] << "' not in '" << result << "'";
    }
    EXPECT_EQ(result.size(), 30);
  }
}

TEST(StreamLimiterGroups, LogGroupsParent) {
  utils::datetime::MockNowSet({});

  StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{20});
  limiter.SetWindowSize(kWindowSize);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  auto halfRange = kTotalRecords / 2;

  // Make sure that we prefer the last group, because chances are high that
  // it will appear in next chunk

  for (size_t i = 0; i < halfRange; ++i) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{i});
    limiter.HandleRecord();
  }
  for (size_t i = halfRange; i < kTotalRecords; ++i) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{i});
    limiter.OnParent(Link{i - halfRange});
    limiter.HandleRecord();
  }
  {
    const auto result1 = limiter.EndChunkAndGetRecordsBatch();
    for (size_t i : {2, 5}) {
      EXPECT_NE(result1.find(kRecords10Bytes[i]), std::string::npos)
          << "'" << kRecords10Bytes[i] << "' not in '" << result1 << "'";
    }
  }

  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // Make sure that the parent group is remembered between
  // `EndChunkAndGetResult` calls

  for (size_t i = halfRange; i < kTotalRecords; ++i) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{i * 10});
    limiter.OnParent(Link{i - halfRange});
    limiter.HandleRecord();
  }
  {
    const auto result1 = limiter.EndChunkAndGetRecordsBatch();
    for (size_t i : {5}) {
      EXPECT_NE(result1.find(kRecords10Bytes[i]), std::string::npos)
          << "'" << kRecords10Bytes[i] << "' not in '" << result1 << "'";
    }
    EXPECT_EQ(result1.size(), 10);
  }

  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // Make sure that the initial link group is remembered between
  // `EndChunkAndGetResult` calls

  for (size_t i = 0; i < halfRange; ++i) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{i});
    limiter.HandleRecord();
  }
  {
    const auto result1 = limiter.EndChunkAndGetRecordsBatch();
    for (size_t i : {2}) {
      EXPECT_NE(result1.find(kRecords10Bytes[i]), std::string::npos)
          << "'" << kRecords10Bytes[i] << "' not in '" << result1 << "'";
    }
    EXPECT_EQ(result1.size(), 10);
  }

  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // Make sure that old group is remembered to ignore between
  // `EndChunkAndGetResult` calls

  limiter.SetMaxOutputSize(utils::BytesPerSecond{30});
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});
  for (size_t i = 0; i < kTotalRecords; ++i) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{i});
    limiter.HandleRecord();
  }

  limiter.NewRecord(std::string(kRecords10Bytes[0]));
  limiter.SetLink(Link{2000});  // New link
  limiter.HandleRecord();

  {
    const auto result1 = limiter.EndChunkAndGetRecordsBatch();
    for (size_t i : {0, 2, 5}) {
      EXPECT_NE(result1.find(kRecords10Bytes[i]), std::string::npos)
          << "'" << kRecords10Bytes[i] << "' not in '" << result1 << "'";
    }
    EXPECT_EQ(result1.size(), 30);
  }
}

TEST(StreamLimiterGroups, FillTheKnapsack1) {
  utils::datetime::MockNowSet({});

  StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{30});
  limiter.SetWindowSize(kWindowSize);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // Make sure that we fill the Knapsack as much as possible in simple cases
  for (size_t i : {0, 1}) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{i});
    limiter.HandleRecord();
  }
  for (size_t i = 2; i < kTotalRecords; ++i) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{2});  // group is larger than 30 bytes
    limiter.HandleRecord();
  }

  const auto result = limiter.EndChunkAndGetRecordsBatch();
  for (auto i : {0, 1}) {
    EXPECT_NE(result.find(kRecords10Bytes[i]), std::string::npos)
        << "'" << kRecords10Bytes[i] << "' not in '" << result << "'";
  }
  EXPECT_EQ(result.size(), 20);
}

TEST(StreamLimiterGroups, FillTheKnapsack2) {
  utils::datetime::MockNowSet({});

  StreamLimiter limiter;
  limiter.SetMaxOutputSize(utils::BytesPerSecond{30});
  limiter.SetWindowSize(kWindowSize);
  limiter.DrainOutputLimit();
  utils::datetime::MockSleep(std::chrono::seconds{1});

  // Make sure that we fill the Knapsack as much as possible in simple cases
  for (size_t i : {0, 1, 2}) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{i == 2 ? 1 : i});
    limiter.HandleRecord();
  }
  for (size_t i = 2; i < kTotalRecords; ++i) {
    limiter.NewRecord(std::string(kRecords10Bytes[i]));
    limiter.SetLink(Link{2});  // group is larger than 30 bytes
    limiter.HandleRecord();
  }

  const auto result = limiter.EndChunkAndGetRecordsBatch();
  for (auto i : {0, 1, 2}) {
    EXPECT_NE(result.find(kRecords10Bytes[i]), std::string::npos)
        << "'" << kRecords10Bytes[i] << "' not in '" << result << "'";
  }
  EXPECT_EQ(result.size(), 30);
}
