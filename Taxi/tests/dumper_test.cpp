#include <gtest/gtest.h>

#include "cache/dumper.hpp"
#include "test_helpers.hpp"

#include <utils/uuid4.hpp>

#include <fstream>
#include <set>

namespace {
const std::string kDumpPath = "/tmp/driver-ratings-dump/";
const std::set<std::string> kDumpSet = {"0_0_9",
                                        "2014-01-09T12:35:34+0000",
                                        "9\t0.123457\t1\t0.123457\t0\t0_0_9",
                                        "7\t0.123457\t1\t0.123457\t0\t0_0_7",
                                        "5\t0.123457\t1\t0.123457\t0\t0_0_5",
                                        "8\t0.123457\t1\t0.123457\t0\t0_0_8",
                                        "6\t0.123457\t1\t0.123457\t0\t0_0_6",
                                        "0\t0.123457\t1\t0.123457\t0\t0_0_0",
                                        "1\t0.123457\t1\t0.123457\t0\t0_0_1",
                                        "2\t0.123457\t1\t0.123457\t0\t0_0_2",
                                        "4\t0.123457\t1\t0.123457\t0\t0_0_4",
                                        "3\t0.123457\t1\t0.123457\t0\t0_0_3"};

models::DriversRatingsMap FillTestMap() {
  models::DriversRatingsMap test_map;
  for (int i = 0; i < 10; ++i) {
    std::string id = std::to_string(i);
    models::DriverRatingInfo info{
        id, false, "0_0_" + id, {0.1234567, 1, 0.1234567}};
    test_map.Emplace(std::move(id), std::move(info));
  }
  test_map.SetLastRevision("0_0_9");
  return test_map;
}
}  // namespace

TEST(DriverRatingsCache, DumpAndRestoreCache) {
  const utils::Async::Status status;
  LogExtra log_extra{utils::generators::Uuid4()};
  auto cache_ptr = std::make_shared<models::DriversRatingsMap>(FillTestMap());
  const auto last_modified = std::chrono::system_clock::from_time_t(1389270934);
  const auto& filename = driver_ratings::dumper::Dump(
      cache_ptr, last_modified, kDumpPath, 1, status, log_extra);
  std::ifstream ifs(filename);
  std::string line;
  std::set<std::string> dump_set;
  while (std::getline(ifs, line)) {
    dump_set.emplace(line);
  }
  ifs.close();
  EXPECT_EQ(dump_set, kDumpSet);
  boost::optional<std::chrono::system_clock::time_point> restored_last_modified;
  const auto restored_cache_ptr = driver_ratings::dumper::Restore(
      kDumpPath, restored_last_modified, log_extra);
  EXPECT_EQ(restored_cache_ptr->GetLastRevision(), "0_0_9");
  ASSERT_TRUE(restored_last_modified != boost::none);
  EXPECT_EQ(last_modified, restored_last_modified);
  const auto& expected_data = cache_ptr->GetConstReferenceToData();
  const auto& restored_data = restored_cache_ptr->GetConstReferenceToData();
  EXPECT_EQ(restored_data, expected_data);
}
