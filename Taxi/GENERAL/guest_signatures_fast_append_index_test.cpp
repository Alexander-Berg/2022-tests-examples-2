#include "guest_signatures_fast_append_index.hpp"

#include <list>
#include <unordered_map>

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

namespace {

using identification::GuestSignaturesFastAppendIndex;
using identification::GuestSignaturesLinearIndex;
using identification::IdentifierGenerator;
using identification::SharedAppendIndex;
using models::identification::Normalize;
using models::identification::Signature;
using std::chrono::milliseconds;
using TimePoint = std::chrono::system_clock::time_point;

struct Tuple {
  std::string name;
  Signature signature;
  TimePoint updated_ts;
};

class SimpleGenerator : public IdentifierGenerator {
 public:
  std::string Generate(
      const models::identification::Signature& signature,
      std::chrono::system_clock::time_point timestamp) override;
  std::vector<Tuple> GetTable() const { return table_; }

 private:
  unsigned counter_{0};
  std::vector<Tuple> table_;
};

std::string SimpleGenerator::Generate(
    const models::identification::Signature& signature,
    std::chrono::system_clock::time_point updated_ts) {
  auto id = std::to_string(counter_++);
  table_.push_back({id, signature, updated_ts});
  return id;
}

const unsigned kDimension = 4;

Signature GenerateSignature() {
  Signature result(kDimension, 0.0f);
  for (unsigned i = 0; i < kDimension; ++i) {
    result[i] = (std::rand() % 100) * 0.1f;
  }
  return result;
}

}  // namespace

UTEST(GuestSignaturesFastAppendIndex, Searching) {
  auto generator = std::make_shared<SimpleGenerator>();

  std::chrono::system_clock::time_point now{};
  utils::datetime::MockNowSet(now);

  // GuestSignaturesLinearIndex linear_index(kDimension);
  auto append_index =
      std::make_shared<SharedAppendIndex>(kDimension, generator);

  for (unsigned i = 0; i < 10; ++i) {
    now += milliseconds(1);
    utils::datetime::MockNowSet(now);
    append_index->AddNewSignature(GenerateSignature());
  }

  std::unique_ptr<GuestSignaturesFastAppendIndex> new_version_index;
  auto initial_index = std::make_unique<GuestSignaturesFastAppendIndex>(
      GuestSignaturesLinearIndex{kDimension}, append_index);
  ASSERT_EQ(initial_index->GetAppendPart().GetSignaturesCount(), 10);
  ASSERT_EQ(initial_index->GetAppendPart().GetChunksCount(), 1);
  ASSERT_EQ(initial_index->GetFixedPart().GetSize(), 0);
  for (const auto& item : generator->GetTable()) {
    const auto result = initial_index->GetSimilar(item.signature, 1);
    ASSERT_EQ(result.size(), 1);
    EXPECT_EQ(result.front().name, item.name);
    EXPECT_TRUE(fabs(result.front().distance) < 5e-7);
  }

  // Step 1. first incremental update of linear index
  // Updating append index with some overlap with linear index
  {
    GuestSignaturesLinearIndex linear_index{kDimension};
    const auto& table = generator->GetTable();
    TimePoint max_updated_ts;
    for (int i = 0; i < 4; ++i) {
      const auto& item = table[i];
      linear_index.Upsert(item.name, {item.signature, item.updated_ts});
      max_updated_ts = std::max(max_updated_ts, item.updated_ts);
    }
    append_index = std::make_shared<SharedAppendIndex>(
        *append_index, max_updated_ts - milliseconds(1));
    new_version_index = std::make_unique<GuestSignaturesFastAppendIndex>(
        std::move(linear_index), append_index);

    ASSERT_EQ(initial_index->GetAppendPart().GetSignaturesCount(), 10);
    ASSERT_EQ(initial_index->GetAppendPart().GetChunksCount(), 2);
    ASSERT_EQ(initial_index->GetFixedPart().GetSize(), 0);
    ASSERT_EQ(new_version_index->GetAppendPart().GetSignaturesCount(), 10);
    ASSERT_EQ(new_version_index->GetAppendPart().GetChunksCount(), 2);
    ASSERT_EQ(new_version_index->GetFixedPart().GetSize(), 4);

    for (const auto& item : generator->GetTable()) {
      const auto result = initial_index->GetSimilar(item.signature, 1);
      ASSERT_EQ(result.size(), 1);
      EXPECT_EQ(result.front().name, item.name);
      EXPECT_TRUE(fabs(result.front().distance) < 5e-7);
    }
    for (const auto& item : generator->GetTable()) {
      const auto result = new_version_index->GetSimilar(item.signature, 1);
      ASSERT_EQ(result.size(), 1);
      EXPECT_EQ(result.front().name, item.name);
      EXPECT_TRUE(fabs(result.front().distance) < 5e-7);
    }
  }

  // Step 3. appending some extra signatures
  {
    for (unsigned i = 10; i < 20; ++i) {
      now += milliseconds(1);
      utils::datetime::MockNowSet(now);
      initial_index->AddNewSignature(GenerateSignature());
    }
    ASSERT_EQ(initial_index->GetAppendPart().GetSignaturesCount(), 20);
    ASSERT_EQ(initial_index->GetAppendPart().GetChunksCount(), 2);
    ASSERT_EQ(initial_index->GetFixedPart().GetSize(), 0);
    ASSERT_EQ(new_version_index->GetAppendPart().GetSignaturesCount(), 20);
    ASSERT_EQ(new_version_index->GetAppendPart().GetChunksCount(), 2);
    ASSERT_EQ(new_version_index->GetFixedPart().GetSize(), 4);

    for (const auto& item : generator->GetTable()) {
      const auto result = initial_index->GetSimilar(item.signature, 1);
      ASSERT_EQ(result.size(), 1);
      EXPECT_EQ(result.front().name, item.name);
      EXPECT_TRUE(fabs(result.front().distance) < 5e-7);
    }
    for (const auto& item : generator->GetTable()) {
      const auto result = new_version_index->GetSimilar(item.signature, 1);
      ASSERT_EQ(result.size(), 1);
      EXPECT_EQ(result.front().name, item.name);
      EXPECT_TRUE(fabs(result.front().distance) < 5e-7);
    }
  }

  initial_index.swap(new_version_index);
  new_version_index.reset();

  // Step 3. second incremental update
  {
    GuestSignaturesLinearIndex linear_index = initial_index->GetFixedPart();
    const auto& table = generator->GetTable();
    TimePoint max_updated_ts;
    for (int i = 4; i < 12; ++i) {
      const auto& item = table[i];
      linear_index.Upsert(item.name, {item.signature, item.updated_ts});
      max_updated_ts = std::max(max_updated_ts, item.updated_ts);
    }
    append_index = std::make_shared<SharedAppendIndex>(
        *append_index, max_updated_ts - milliseconds(1));
    new_version_index = std::make_unique<GuestSignaturesFastAppendIndex>(
        std::move(linear_index), append_index);

    ASSERT_EQ(initial_index->GetAppendPart().GetSignaturesCount(), 20);
    ASSERT_EQ(initial_index->GetAppendPart().GetChunksCount(), 3);
    ASSERT_EQ(initial_index->GetFixedPart().GetSize(), 4);
    ASSERT_EQ(new_version_index->GetAppendPart().GetSignaturesCount(), 10);
    ASSERT_EQ(new_version_index->GetAppendPart().GetChunksCount(), 2);
    ASSERT_EQ(new_version_index->GetFixedPart().GetSize(), 12);

    for (const auto& item : generator->GetTable()) {
      const auto result = initial_index->GetSimilar(item.signature, 1);
      ASSERT_EQ(result.size(), 1);
      EXPECT_EQ(result.front().name, item.name);
      EXPECT_TRUE(fabs(result.front().distance) < 5e-7);
    }
    for (const auto& item : generator->GetTable()) {
      const auto result = new_version_index->GetSimilar(item.signature, 1);
      ASSERT_EQ(result.size(), 1);
      EXPECT_EQ(result.front().name, item.name);
      EXPECT_TRUE(fabs(result.front().distance) < 5e-7);
    }
  }

  initial_index.swap(new_version_index);
  new_version_index.reset();

  // Step 4. third incremental update
  {
    GuestSignaturesLinearIndex linear_index = initial_index->GetFixedPart();
    const auto& table = generator->GetTable();
    TimePoint max_updated_ts;
    for (int i = 0; i < 20; ++i) {
      const auto& item = table[i];
      linear_index.Upsert(item.name, {item.signature, item.updated_ts});
      max_updated_ts = std::max(max_updated_ts, item.updated_ts);
    }
    append_index = std::make_shared<SharedAppendIndex>(
        *append_index, max_updated_ts + milliseconds(1));
    new_version_index = std::make_unique<GuestSignaturesFastAppendIndex>(
        std::move(linear_index), append_index);

    ASSERT_EQ(initial_index->GetAppendPart().GetSignaturesCount(), 10);
    ASSERT_EQ(initial_index->GetAppendPart().GetChunksCount(), 3);
    ASSERT_EQ(initial_index->GetFixedPart().GetSize(), 12);
    ASSERT_EQ(new_version_index->GetAppendPart().GetSignaturesCount(), 0);
    ASSERT_EQ(new_version_index->GetAppendPart().GetChunksCount(), 1);
    ASSERT_EQ(new_version_index->GetFixedPart().GetSize(), 20);

    for (const auto& item : generator->GetTable()) {
      const auto result = initial_index->GetSimilar(item.signature, 1);
      ASSERT_EQ(result.size(), 1);
      EXPECT_EQ(result.front().name, item.name);
      EXPECT_TRUE(fabs(result.front().distance) < 5e-7);
    }
    for (const auto& item : generator->GetTable()) {
      const auto result = new_version_index->GetSimilar(item.signature, 1);
      ASSERT_EQ(result.size(), 1);
      EXPECT_EQ(result.front().name, item.name);
      EXPECT_TRUE(fabs(result.front().distance) < 5e-7);
    }
  }
}
