#include "guest_signatures_linear_index.hpp"

#include <list>
#include <unordered_map>

#include <userver/utest/utest.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

namespace {

using identification::GuestSignaturesLinearIndex;
using models::guest_signatures::Storage;
using models::identification::Signature;
using std::chrono::milliseconds;
using TimePoint = std::chrono::system_clock::time_point;

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

UTEST(GuestSignaturesLinearIndexTest, UpsertAndGetSimilar) {
  utils::datetime::MockNowUnset();

  GuestSignaturesLinearIndex index(kDimension);

  std::unordered_map<std::string, Signature> table;

  for (unsigned i = 0; i < 100; ++i) {
    auto input = GenerateSignature();
    auto id = std::to_string(i);
    index.Upsert(id, {input, utils::datetime::Now()});
    table.insert_or_assign(std::move(id), std::move(input));
  }

  EXPECT_EQ(index.GetSize(), 100);

  for (const auto& [id, signature] : table) {
    auto result = index.GetSimilar(signature, 1);
    EXPECT_EQ(result.size(), 1);
    EXPECT_EQ(result.front().name, id);
    EXPECT_TRUE(fabs(result.front().distance) < 3e-7);
  }
}

UTEST(GuestSignaturesLinearIndexTest, PartialCopy) {
  utils::datetime::MockNowUnset();

  GuestSignaturesLinearIndex index(kDimension);

  Storage table;
  TimePoint now = std::chrono::system_clock::now();
  const TimePoint younger_than_ts = now + milliseconds(50);
  utils::datetime::MockNowSet(now);

  for (unsigned i = 0; i < 100; ++i) {
    auto input = GenerateSignature();
    auto id = std::to_string(i);
    Storage::mapped_type item{std::move(input), utils::datetime::Now()};
    index.Upsert(id, item);
    now += milliseconds(1);
    utils::datetime::MockNowSet(now);
    table.insert_or_assign(std::move(id), std::move(item));
  }

  GuestSignaturesLinearIndex new_index(index, younger_than_ts);
  EXPECT_EQ(index.GetSize(), 100);
  EXPECT_EQ(new_index.GetSize(), 50);

  for (const auto& [id, item] : table) {
    auto result = new_index.GetSimilar(item.signature, 1);
    EXPECT_EQ(result.size(), 1);

    if (item.updated_ts >= younger_than_ts) {
      EXPECT_EQ(result.front().name, id);
      EXPECT_TRUE(fabs(result.front().distance) < 3e-7);
    } else {
      EXPECT_NE(result.front().name, id);
    }
  }
}
