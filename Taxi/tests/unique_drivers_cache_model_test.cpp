#include <gtest/gtest.h>

#include <userver/dump/test_helpers.hpp>

#include <api_base/unique_drivers_cache_model.hpp>
#include <api_base/utils.hpp>

namespace {

using namespace api_over_db::models;
using namespace api_over_db::utils;
using namespace std::string_literals;

using IdMapByTimestamp = std::map<formats::bson::Timestamp, std::string>;

template <class T>
std::string ExtractId(const T& item) {
  return item->id.GetUnderlying();
}

template <class T>
IdMapByTimestamp ExtractIdAndRemap(
    const std::map<formats::bson::Timestamp, T>& items) {
  IdMapByTimestamp result;

  for (const auto& [timestamp, data] : items) {
    result.emplace(timestamp, ExtractId(data));
  }

  return result;
}

std::vector<std::string> ExtractIdAndSort(
    const std::vector<DriverProfileCPtr>& driver_profiles) {
  std::vector<std::string> result;
  result.reserve(driver_profiles.size());

  for (const auto& driver_profile : driver_profiles) {
    result.push_back(ExtractId(driver_profile));
  }
  std::sort(result.begin(), result.end());

  return result;
}

}  // namespace

TEST(MultiplexerCacheModel, CacheInsertions) {
  UniqueDriversCacheModel cache_model{false};

  cache_model.UpsertUniqueDriver("id_dp_1", {"license_1"},
                                 ParseTimestamp("1_1"), false);
  cache_model.UpsertUniqueDriver("id_ud_2", {"license_2", "license_3"},
                                 ParseTimestamp("2_1"), false);
  cache_model.SetUniqueDriversLastRevision(ParseTimestamp("2_1"));

  EXPECT_EQ(cache_model.UniqueDriversSize(), 2);

  cache_model.UpsertDriverProfile("id_dp_1", {"license_1"s},
                                  ParseTimestamp("1_1"), false);
  cache_model.UpsertDriverProfile("id_dp_2", {"license_2"s},
                                  ParseTimestamp("2_1"), false);
  cache_model.UpsertDriverProfile("id_dp_3", {"license_3"s},
                                  ParseTimestamp("2_2"), false);
  cache_model.SetDriverProfilesLastRevision(ParseTimestamp("2_2"));
  EXPECT_EQ(cache_model.DriverProfilesSize(), 3);
  EXPECT_EQ(cache_model.Size(), 5);

  EXPECT_EQ(TimestampToString(cache_model.GetUniqueDriversLastRevision()),
            "2_1");
  EXPECT_EQ(TimestampToString(cache_model.GetDriverProfilesLastRevision()),
            "2_2");
}

TEST(MultiplexerCacheModel, CacheExcluding) {
  UniqueDriversCacheModel cache_model{false};

  cache_model.UpsertUniqueDriver("id_ud_1", {"license_1"},
                                 ParseTimestamp("1_1"), false);
  cache_model.UpsertUniqueDriver("id_ud_2", {"license_2", "license_3"},
                                 ParseTimestamp("2_1"), false);
  cache_model.SetUniqueDriversLastRevision(ParseTimestamp("2_1"));
  EXPECT_EQ(cache_model.UniqueDriversSize(), 2);

  cache_model.UpsertDriverProfile("id_dp_1", {"license_1"s},
                                  ParseTimestamp("1_1"), false);
  cache_model.UpsertDriverProfile("id_dp_2", {"license_2"s},
                                  ParseTimestamp("2_1"), false);
  cache_model.UpsertDriverProfile("id_dp_3", {"license_3"s},
                                  ParseTimestamp("2_2"), false);
  cache_model.SetDriverProfilesLastRevision(ParseTimestamp("2_2"));
  EXPECT_EQ(cache_model.DriverProfilesSize(), 3);

  EXPECT_EQ(cache_model.Size(), 5);

  cache_model.UpsertUniqueDriver("id_ud_1", {}, ParseTimestamp("0_0"), true);
  EXPECT_EQ(cache_model.UniqueDriversSize(), 1);
  EXPECT_EQ(cache_model.Size(), 4);

  cache_model.UpsertUniqueDriver("unknown", {}, ParseTimestamp("0_0"), true);
  EXPECT_EQ(cache_model.UniqueDriversSize(), 1);
  EXPECT_EQ(cache_model.Size(), 4);

  cache_model.UpsertDriverProfile("id_dp_2", {}, ParseTimestamp("0_0"), true);
  EXPECT_EQ(cache_model.DriverProfilesSize(), 2);
  EXPECT_EQ(cache_model.Size(), 3);

  cache_model.UpsertDriverProfile("unknown", {}, ParseTimestamp("0_0"), true);
  EXPECT_EQ(cache_model.DriverProfilesSize(), 2);
  EXPECT_EQ(cache_model.Size(), 3);

  EXPECT_EQ(TimestampToString(cache_model.GetUniqueDriversLastRevision()),
            "2_1");
  EXPECT_EQ(TimestampToString(cache_model.GetDriverProfilesLastRevision()),
            "2_2");
}

TEST(MultiplexerCacheModel, CacheLicenseMatching) {
  UniqueDriversCacheModel cache_model{false};

  cache_model.UpsertUniqueDriver("id_ud_1", {"license_1"},
                                 ParseTimestamp("1_1"), false);
  cache_model.UpsertUniqueDriver("id_ud_2", {"license_2", "license_3"},
                                 ParseTimestamp("2_1"), false);
  cache_model.UpsertUniqueDriver("id_ud_3", {"license_4"},
                                 ParseTimestamp("2_2"), false);
  cache_model.UpsertUniqueDriver("id_ud_4", {"license_6"},
                                 ParseTimestamp("3_1"), false);
  cache_model.SetUniqueDriversLastRevision(ParseTimestamp("3_1"));

  cache_model.UpsertDriverProfile("id_dp_1", {"license_1"s},
                                  ParseTimestamp("1_1"), false);
  cache_model.UpsertDriverProfile("id_dp_2", {"license_2"s},
                                  ParseTimestamp("2_1"), false);
  cache_model.UpsertDriverProfile("id_dp_3", {"license_3"s},
                                  ParseTimestamp("2_2"), false);
  cache_model.UpsertDriverProfile("id_dp_4", {"license_5"s},
                                  ParseTimestamp("2_3"), false);
  cache_model.UpsertDriverProfile("id_dp_5", {"license_6"s},
                                  ParseTimestamp("3_1"), false);
  cache_model.UpsertDriverProfile("id_dp_6", {"license_6"s},
                                  ParseTimestamp("4_1"), false);
  cache_model.SetDriverProfilesLastRevision(ParseTimestamp("4_1"));

  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_1")->id.GetUnderlying(),
      "id_ud_1");
  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_3")->id.GetUnderlying(),
      "id_ud_2");
  EXPECT_EQ(cache_model.GetUniqueDriverByDriverProfile("id_dp_4"), nullptr);

  EXPECT_EQ(
      ExtractIdAndSort(cache_model.GetDriverProfilesByUniqueDriver("id_ud_1")),
      (std::vector<std::string>{"id_dp_1"}));
  EXPECT_EQ(
      ExtractIdAndSort(cache_model.GetDriverProfilesByUniqueDriver("id_ud_2")),
      (std::vector<std::string>{"id_dp_2", "id_dp_3"}));
  EXPECT_EQ(
      ExtractIdAndSort(cache_model.GetDriverProfilesByUniqueDriver("id_ud_3")),
      (std::vector<std::string>{}));
  EXPECT_EQ(
      ExtractIdAndSort(cache_model.GetDriverProfilesByUniqueDriver("id_ud_4")),
      (std::vector<std::string>{"id_dp_5", "id_dp_6"}));
}

TEST(MultiplexerCacheModel, LicenseChanging) {
  UniqueDriversCacheModel cache_model{false};

  cache_model.UpsertUniqueDriver("id_ud_1", {"license_1"},
                                 ParseTimestamp("1_1"), false);
  cache_model.UpsertUniqueDriver("id_ud_2", {"license_2"},
                                 ParseTimestamp("2_1"), false);
  cache_model.SetUniqueDriversLastRevision(ParseTimestamp("2_1"));

  cache_model.UpsertDriverProfile("id_dp_1", {"license_1"s},
                                  ParseTimestamp("1_1"), false);
  cache_model.UpsertDriverProfile("id_dp_2", {"license_1"s},
                                  ParseTimestamp("2_1"), false);
  cache_model.UpsertDriverProfile("id_dp_2", {"license_2"s},
                                  ParseTimestamp("3_1"), false);
  cache_model.SetDriverProfilesLastRevision(ParseTimestamp("3_1"));

  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_1")->id.GetUnderlying(),
      "id_ud_1");
  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_2")->id.GetUnderlying(),
      "id_ud_2");

  EXPECT_EQ(
      ExtractIdAndSort(cache_model.GetDriverProfilesByUniqueDriver("id_ud_1")),
      (std::vector<std::string>{"id_dp_1"}));
  EXPECT_EQ(
      ExtractIdAndSort(cache_model.GetDriverProfilesByUniqueDriver("id_ud_2")),
      (std::vector<std::string>{"id_dp_2"}));

  cache_model.UpsertDriverProfile("id_dp_1", {"license_2"s},
                                  ParseTimestamp("4_1"), false);

  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_1")->id.GetUnderlying(),
      "id_ud_2");
  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_2")->id.GetUnderlying(),
      "id_ud_2");

  EXPECT_EQ(
      ExtractIdAndSort(cache_model.GetDriverProfilesByUniqueDriver("id_dp_1")),
      (std::vector<std::string>{}));
  EXPECT_EQ(
      ExtractIdAndSort(cache_model.GetDriverProfilesByUniqueDriver("id_ud_2")),
      (std::vector<std::string>{"id_dp_1", "id_dp_2"}));
}

TEST(MultiplexerCacheModel, CacheTimestampIndexing) {
  UniqueDriversCacheModel cache_model{true};

  cache_model.UpsertUniqueDriver("id_ud_1", {"license_1"},
                                 ParseTimestamp("1_1"), false);
  cache_model.UpsertUniqueDriver("id_ud_2", {"license_2", "license_3"},
                                 ParseTimestamp("2_1"), false);
  cache_model.SetUniqueDriversLastRevision(ParseTimestamp("2_1"));
  cache_model.UpsertUniqueDriver("id_ud_3", {"license_4"},
                                 ParseTimestamp("2_2"), false);

  cache_model.UpsertDriverProfile("id_dp_1", {"license_1"s},
                                  ParseTimestamp("1_1"), false);
  cache_model.UpsertDriverProfile("id_dp_2", {"license_2"s},
                                  ParseTimestamp("2_1"), false);
  cache_model.UpsertDriverProfile("id_dp_3", {"license_3"s},
                                  ParseTimestamp("2_2"), false);
  cache_model.SetDriverProfilesLastRevision(ParseTimestamp("2_2"));
  cache_model.UpsertDriverProfile("id_dp_4", {"license_5"s},
                                  ParseTimestamp("2_3"), false);

  const auto unique_driver_result_1 = IdMapByTimestamp{
      {ParseTimestamp("1_1"), "id_ud_1"}, {ParseTimestamp("2_1"), "id_ud_2"}};
  EXPECT_EQ(ExtractIdAndRemap(cache_model.BuildUniqueDriverMapByTimestamp(
                ParseTimestamp("0_0"), 2)),
            unique_driver_result_1);

  const auto unique_driver_result_2 =
      IdMapByTimestamp{{ParseTimestamp("2_1"), "id_ud_2"}};
  EXPECT_EQ(ExtractIdAndRemap(cache_model.BuildUniqueDriverMapByTimestamp(
                ParseTimestamp("1_2"), 123, true)),
            unique_driver_result_2);

  const auto unique_driver_result_3 = IdMapByTimestamp{
      {ParseTimestamp("2_1"), "id_ud_2"}, {ParseTimestamp("2_2"), "id_ud_3"}};
  EXPECT_EQ(ExtractIdAndRemap(cache_model.BuildUniqueDriverMapByTimestamp(
                ParseTimestamp("1_2"), 123, false)),
            unique_driver_result_3);

  const auto driver_profile_result_1 = IdMapByTimestamp{
      {ParseTimestamp("2_1"), "id_dp_2"}, {ParseTimestamp("2_2"), "id_dp_3"}};
  EXPECT_EQ(ExtractIdAndRemap(cache_model.BuildDriverProfilesMapByTimestamp(
                ParseTimestamp("1_1"), 2)),
            driver_profile_result_1);

  const auto driver_profile_result_2 = IdMapByTimestamp{
      {ParseTimestamp("2_1"), "id_dp_2"}, {ParseTimestamp("2_2"), "id_dp_3"}};
  EXPECT_EQ(ExtractIdAndRemap(cache_model.BuildDriverProfilesMapByTimestamp(
                ParseTimestamp("1_1"), 123, true)),
            driver_profile_result_2);

  const auto driver_profile_result_3 =
      IdMapByTimestamp{{ParseTimestamp("2_1"), "id_dp_2"},
                       {ParseTimestamp("2_2"), "id_dp_3"},
                       {ParseTimestamp("2_3"), "id_dp_4"}};
  EXPECT_EQ(ExtractIdAndRemap(cache_model.BuildDriverProfilesMapByTimestamp(
                ParseTimestamp("1_1"), 123, false)),
            driver_profile_result_3);
}

TEST(MultiplexerCacheModel, MultiLicenses) {
  UniqueDriversCacheModel cache_model{true};

  cache_model.UpsertUniqueDriver("id_ud_1", {"license_1"},
                                 ParseTimestamp("1_1"), false);
  cache_model.UpsertUniqueDriver("id_ud_2", {"license_2", "license_1"},
                                 ParseTimestamp("2_1"), false);
  cache_model.UpsertUniqueDriver("id_ud_3", {"license_4"},
                                 ParseTimestamp("2_2"), false);
  cache_model.SetUniqueDriversLastRevision(ParseTimestamp("2_2"));

  cache_model.UpsertDriverProfile("id_dp_1", {"license_1"s},
                                  ParseTimestamp("1_1"), false);
  cache_model.UpsertDriverProfile("id_dp_2", {"license_2"s},
                                  ParseTimestamp("2_1"), false);
  cache_model.UpsertDriverProfile("id_dp_3", {"license_3"s},
                                  ParseTimestamp("2_2"), false);
  cache_model.UpsertDriverProfile("id_dp_4", {"license_1"s},
                                  ParseTimestamp("2_3"), false);
  cache_model.SetDriverProfilesLastRevision(ParseTimestamp("2_3"));

  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_1")->id.GetUnderlying(),
      "id_ud_2");
  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_2")->id.GetUnderlying(),
      "id_ud_2");
  EXPECT_EQ(cache_model.GetUniqueDriverByDriverProfile("id_dp_3"), nullptr);
  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_4")->id.GetUnderlying(),
      "id_ud_2");

  cache_model.UpsertUniqueDriver("id_ud_2", {"license_2", "license_1"},
                                 ParseTimestamp("3_1"), true);

  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_1")->id.GetUnderlying(),
      "id_ud_1");
  EXPECT_EQ(cache_model.GetUniqueDriverByDriverProfile("id_dp_2"), nullptr);
  EXPECT_EQ(cache_model.GetUniqueDriverByDriverProfile("id_dp_3"), nullptr);
  EXPECT_EQ(
      cache_model.GetUniqueDriverByDriverProfile("id_dp_4")->id.GetUnderlying(),
      "id_ud_1");
}

TEST(MultiplexerCacheModel, CacheConfigIndexException) {
  UniqueDriversCacheModel cache_model{false};

  cache_model.UpsertUniqueDriver("id_ud_1", {"license_1"},
                                 ParseTimestamp("1_1"), false);
  cache_model.SetUniqueDriversLastRevision(ParseTimestamp("1_1"));
  cache_model.UpsertDriverProfile("id_dp_1", {"license_1"s},
                                  ParseTimestamp("1_1"), false);
  cache_model.SetDriverProfilesLastRevision(ParseTimestamp("1_1"));

  EXPECT_THROW(
      cache_model.BuildUniqueDriverMapByTimestamp(ParseTimestamp("0_0"), 2),
      std::runtime_error);

  EXPECT_THROW(
      cache_model.BuildDriverProfilesMapByTimestamp(ParseTimestamp("2_1"), 123),
      std::runtime_error);
}

TEST(MultiplexerCacheModel, DumpRestoreEmpty) {
  dump::TestWriteReadCycle(UniqueDriversCacheModel{false});
  dump::TestWriteReadCycle(UniqueDriversCacheModel{true});
}

TEST(MultiplexerCacheModel, DumpRestore) {
  UniqueDriversCacheModel cache_model{true};

  cache_model.UpsertUniqueDriver("id_ud_1", {"license_1"},
                                 ParseTimestamp("1_1"), false);
  cache_model.UpsertUniqueDriver("id_ud_2", {"license_2", "license_3"},
                                 ParseTimestamp("2_1"), false);
  cache_model.SetUniqueDriversLastRevision(ParseTimestamp("2_1"));
  cache_model.UpsertUniqueDriver("id_ud_3", {"license_4"},
                                 ParseTimestamp("2_2"), false);

  cache_model.UpsertDriverProfile("id_dp_1", {"license_1"s},
                                  ParseTimestamp("1_1"), false);
  cache_model.UpsertDriverProfile("id_dp_2", {"license_2"s},
                                  ParseTimestamp("2_1"), false);
  cache_model.UpsertDriverProfile("id_dp_3", {"license_3"s},
                                  ParseTimestamp("2_2"), false);
  cache_model.SetDriverProfilesLastRevision(ParseTimestamp("2_2"));
  cache_model.UpsertDriverProfile("id_dp_4", {"license_5"s},
                                  ParseTimestamp("2_3"), false);

  dump::TestWriteReadCycle(cache_model);
}
