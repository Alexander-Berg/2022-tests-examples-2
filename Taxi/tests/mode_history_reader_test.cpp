#include <algorithm>
#include <vector>

#include <userver/utest/utest.hpp>

#include <userver/formats/json/value_builder.hpp>

#include <clients/driver-mode-index/client_mock_base.hpp>

#include <helpers/driver_mode_index.hpp>
#include <helpers/mode_history_reader.hpp>

namespace dmi = ::clients::driver_mode_index;
using namespace formats::json;

class MyDmiClient : public dmi::ClientMockBase {
  static constexpr char kOffset[] = "offset";

 public:
  MyDmiClient(const uint32_t availible_offers) {
    entries_.reserve(availible_offers);
    for (uint32_t i = 0; i < availible_offers; ++i) {
      dmi::HistoryEntry entry{};
      entry.external_event_ref = driver_mode::IdempotencyKey{std::to_string(i)};
      entries_.emplace_back(std::move(entry));
    }
  }

  void ResetRequests() const { requests_.clear(); }

  dmi::v1_mode_history::post::Response V1ModeHistory(
      const dmi::v1_mode_history::post::Request& request,
      const dmi::CommandControl& /*command_control*/ = {}) const override {
    requests_.push_back(request);

    const uint64_t count = request.body.limit;
    const uint64_t offset = std::min<uint64_t>(
        request.body.cursor ? std::stoull(*request.body.cursor) : uint64_t{0},
        entries_.size());
    const auto end_offset = std::min<uint64_t>(offset + count, entries_.size());

    dmi::v1_mode_history::post::Response response{};

    response.docs.insert(response.docs.begin(), entries_.begin() + offset,
                         entries_.begin() + end_offset);

    ValueBuilder cursor_builder;
    cursor_builder[kOffset] = end_offset;
    response.cursor = std::to_string(end_offset);

    return response;
  }

  mutable std::vector<dmi::v1_mode_history::post::Request> requests_;

 private:
  std::vector<dmi::HistoryEntry> entries_;
};

class ModeHistoryReaderIteratorParametrized
    : public testing::Test,
      public testing::WithParamInterface<std::tuple<int, int>> {};

template <typename Client, typename Reader>
void CheckReader1(const Client& client, Reader& reader, int entity_count,
                  uint8_t bulk_size) {
  // iterate with requests
  {
    int64_t id_cursor = 0;
    auto begin = reader.begin();
    while (begin != reader.end()) {
      ASSERT_EQ(begin->external_event_ref,
                driver_mode::IdempotencyKey{std::to_string(id_cursor)});
      ASSERT_LT(id_cursor, entity_count);
      ++begin;
      ++id_cursor;
    }

    ASSERT_EQ(client.requests_.size(),
              bulk_size == 0 ? 1 : ((entity_count + bulk_size) / bulk_size));

    client.ResetRequests();
  }

  // reiterate
  {
    int64_t id_cursor = 0;
    for (const auto& entity : reader) {
      ASSERT_EQ(entity.external_event_ref,
                driver_mode::IdempotencyKey{std::to_string(id_cursor)});
      ASSERT_LT(id_cursor, entity_count);
      ++id_cursor;
    }

    ASSERT_EQ(client.requests_.size(), 0);

    client.ResetRequests();
  }

  // simultanious iteration
  {
    int64_t id_cursor = 0;
    auto begin1 = reader.begin();
    auto begin2 = begin1;
    while (begin1 != reader.end() && begin2 != reader.end()) {
      ASSERT_EQ(begin1, begin2);
      ASSERT_EQ(begin1->external_event_ref,
                driver_mode::IdempotencyKey{std::to_string(id_cursor)});
      ASSERT_LT(id_cursor, entity_count);
      ++begin1;
      ASSERT_NE(begin1, begin2);
      ++begin2;
      ++id_cursor;
    }

    ASSERT_EQ(client.requests_.size(), 0);
  }
}

template <typename Client, typename Reader>
void CheckReader2(const Client& client, Reader& reader, int entity_count,
                  uint8_t bulk_size) {
  int64_t id_cursor = 0;
  auto begin1 = reader.begin();
  auto begin2 = begin1;
  while (begin1 != reader.end() && begin2 != reader.end()) {
    ASSERT_EQ(begin1, begin2);
    ASSERT_EQ(begin1->external_event_ref,
              driver_mode::IdempotencyKey{std::to_string(id_cursor)});
    ASSERT_LT(id_cursor, entity_count);
    ++begin1;
    ASSERT_NE(begin1, begin2);
    ++begin2;
    ++id_cursor;
  }

  ASSERT_EQ(client.requests_.size(),
            bulk_size == 0 ? 1 : ((entity_count + bulk_size) / bulk_size));
}

TEST_P(ModeHistoryReaderIteratorParametrized, Iterate) {
  int entity_count = 0;
  uint8_t bulk_size = 0;
  std::tie(entity_count, bulk_size) = GetParam();

  MyDmiClient dmi_client_mock(entity_count);
  helpers::ModeHistoryReader dmi_reader{
      helpers::driver_mode_index::MakeModeHistoryRequest("park0", "uuid0").body,
      dmi_client_mock, bulk_size};
  CheckReader1(dmi_client_mock, dmi_reader, entity_count, bulk_size);
}

TEST_P(ModeHistoryReaderIteratorParametrized, Iterate2Readers) {
  int entity_count = 0;
  uint8_t bulk_size = 0;
  std::tie(entity_count, bulk_size) = GetParam();
  // simultaneous iteration with reads

  MyDmiClient dmi_client_mock(entity_count);
  helpers::ModeHistoryReader dmi_reader{
      helpers::driver_mode_index::MakeModeHistoryRequest("park0", "uuid0").body,
      dmi_client_mock, bulk_size};
  CheckReader2(dmi_client_mock, dmi_reader, entity_count, bulk_size);
}

INSTANTIATE_TEST_SUITE_P(ModeHistoryReaderIterator,
                         ModeHistoryReaderIteratorParametrized,
                         testing::Combine(testing::Range(0, 10),
                                          testing::Range(0, 15)));
