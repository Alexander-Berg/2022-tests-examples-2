#include "shared_append_index.hpp"

#include <list>
#include <unordered_map>

#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

namespace {

using identification::IdentifierGenerator;
using identification::SharedAppendIndex;
using models::identification::Normalize;
using models::identification::Signature;
using std::chrono::milliseconds;
using TimePoint = std::chrono::system_clock::time_point;

class SimpleGenerator : public IdentifierGenerator {
 public:
  std::string Generate(
      const models::identification::Signature& signature,
      std::chrono::system_clock::time_point timestamp) override;

 private:
  unsigned counter_{0};
};

std::string SimpleGenerator::Generate(const models::identification::Signature&,
                                      std::chrono::system_clock::time_point) {
  return std::to_string(counter_++);
}

const unsigned kDimension = 4;

Signature GenerateSignature() {
  Signature result(kDimension, 0.0f);
  for (unsigned i = 0; i < kDimension; ++i) {
    result[i] = (std::rand() % 100) * 0.1f;
  }
  return result;
}

struct Tuple {
  std::string name;
  Signature signature;
};

}  // namespace

UTEST(ShareAppendIndexTest, AppendTest) {
  utils::datetime::MockNowUnset();

  auto generator = std::make_shared<SimpleGenerator>();

  identification::SharedAppendIndex index(kDimension, generator);

  std::unordered_map<std::string, Signature> table;

  for (unsigned i = 0; i < 100; ++i) {
    auto input = GenerateSignature();
    auto id = index.AddNewSignature(input);
    table.insert_or_assign(std::move(id), std::move(input));
  }

  for (const auto& [id, signature] : table) {
    auto result = index.GetSimilar(signature, 1);
    EXPECT_FALSE(result.empty());
    EXPECT_EQ(result.size(), 1);
    EXPECT_EQ(result.front().name, id);
    EXPECT_TRUE(fabs(result.front().distance) < 3e-7);
  }
}

UTEST(ShareAppendIndexTest, AppendTestWithNewChunks) {
  utils::datetime::MockNowUnset();

  auto generator = std::make_shared<SimpleGenerator>();

  identification::SharedAppendIndex index(kDimension, generator);

  std::unordered_map<std::string, Signature> table;

  unsigned chunks_count = 1;
  for (unsigned i = 0; i < 100; ++i) {
    if (i && i % 10 == 0) {
      identification::SharedAppendIndex new_index(
          index, std::chrono::system_clock::time_point());
      ++chunks_count;
      ASSERT_EQ(index.GetChunksCount(), chunks_count);
      ASSERT_EQ(new_index.GetChunksCount(), chunks_count);
    }
    ASSERT_EQ(index.GetChunksCount(), chunks_count);

    auto input = GenerateSignature();
    auto id = index.AddNewSignature(input);
    table.insert_or_assign(std::move(id), std::move(input));
  }

  for (const auto& [id, signature] : table) {
    auto result = index.GetSimilar(signature, 1);
    EXPECT_FALSE(result.empty());
    EXPECT_EQ(result.size(), 1);
    EXPECT_EQ(result.front().name, id);
    EXPECT_TRUE(fabs(result.front().distance) < 3e-7);
  }
}

UTEST(ShareAppendIndexTest, Chunking) {
  auto generator = std::make_shared<SimpleGenerator>();

  identification::SharedAppendIndex index(kDimension, generator);

  std::chrono::system_clock::time_point now{};
  std::vector<Tuple> table;
  utils::datetime::MockNowSet(now);

  std::list<identification::SharedAppendIndex> new_indexes;
  unsigned chunks_count = 1;
  for (unsigned i = 0; i < 100; ++i) {
    now += milliseconds(1);
    utils::datetime::MockNowSet(now);

    if (i && i % 10 == 0) {
      new_indexes.emplace_back(index, now + milliseconds(1));
      ++chunks_count;
      ASSERT_EQ(index.GetChunksCount(), chunks_count);
      ASSERT_EQ(new_indexes.back().GetChunksCount(), 1);
    }
    ASSERT_EQ(index.GetChunksCount(), chunks_count);

    auto input = GenerateSignature();
    auto id = index.AddNewSignature(input);
    table.push_back({std::move(id), std::move(input)});
  }

  unsigned signatures_count = 100;
  ASSERT_EQ(index.GetSignaturesCount(), 100);
  for (const auto& new_index : new_indexes) {
    signatures_count -= 10;
    ASSERT_EQ(new_index.GetSignaturesCount(), signatures_count);
    ASSERT_EQ(new_index.GetChunksCount(), signatures_count / 10);
  }

  for (unsigned i = 0; i < table.size(); ++i) {
    const auto& item = table[i];
    auto result = index.GetSimilar(item.signature, 1);
    EXPECT_FALSE(result.empty());
    EXPECT_EQ(result.size(), 1);
    EXPECT_EQ(result.front().name, item.name);
    EXPECT_TRUE(fabs(result.front().distance) < 3e-7);

    unsigned max_new_idx = i / 10;
    unsigned new_index_num = 0;
    for (const auto& new_index : new_indexes) {
      auto result = new_index.GetSimilar(item.signature, 1);
      if (new_index_num >= max_new_idx) {
        EXPECT_FALSE(result.empty());
        EXPECT_EQ(result.size(), 1);
        EXPECT_NE(result.front().name, item.name);
      } else {
        EXPECT_FALSE(result.empty());
        EXPECT_EQ(result.size(), 1);
        EXPECT_EQ(result.front().name, item.name);
        EXPECT_TRUE(fabs(result.front().distance) < 3e-7);
      }
      ++new_index_num;
    }
  }

  utils::datetime::MockNowUnset();
}
