#include <userver/utest/utest.hpp>

#include <taxi_config/parks-activation-client/taxi_config.hpp>
#include <userver/cache/statistics_mock.hpp>
#include <userver/dynamic_config/snapshot.hpp>
#include <userver/formats/json.hpp>
#include <userver/utils/datetime.hpp>
#include <userver/utils/mock_now.hpp>

#include <dump/cache_dumper.hpp>
#include <models/park_activation.hpp>

#include <userver/logging/log.hpp>

namespace {

const std::chrono::seconds kDumpTtlDefault = std::chrono::seconds(10 * 60);
const std::chrono::seconds kMinUpdateInterval = std::chrono::seconds(1 * 4);

class MockDumperConfig : public parks_activation::utils::CacheDumperConfig {
 public:
  std::chrono::seconds GetDumpTtl() const override { return dump_ttl_; }
  std::chrono::seconds GetMinUpdateInterval() const override {
    return min_update_interval_;
  }

 private:
  std::chrono::seconds dump_ttl_{kDumpTtlDefault};
  std::chrono::seconds min_update_interval_{kMinUpdateInterval};
};

class DumperWrapper {
 public:
  DumperWrapper(const std::string& dump_path) {
    dumper_ = parks_activation::utils::CreateStreamDumper(
        std::make_unique<MockDumperConfig>(), dump_path);
    dumper_->Clear();
  }

  virtual ~DumperWrapper() { dumper_->Clear(); }

  bool Load(parks_activation::models::Model& model) {
    return dumper_->Load(model);
  }

  bool Store(const parks_activation::models::Model& model) {
    return dumper_->Store(model);
  }

 private:
  std::unique_ptr<parks_activation::utils::CacheDumper> dumper_;
};

std::unique_ptr<DumperWrapper> CreateDumper() {
  std::string dump_path = "/tmp/parks-activation-dump/";
  std::unique_ptr<DumperWrapper> dumper =
      std::unique_ptr<DumperWrapper>(new DumperWrapper(dump_path));
  return dumper;
}

parks_activation::models::Park CreateTestItem(
    long revision, std::chrono::system_clock::time_point time_point =
                       ::utils::datetime::Now()) {
  parks_activation::models::Park test_item;
  test_item.park_id = std::to_string(revision);
  test_item.update_info.revision = revision;
  test_item.update_info.last_modified = time_point;
  return test_item;
}

auto ToTie(const parks_activation::models::Park& park) {
  return std::tie(park.park_id, park.city_id, park.deactivated,
                  park.deactivated_reason, park.can_cash, park.can_card,
                  park.can_corp, park.can_coupon, park.can_logistic,
                  park.can_corp_without_vat, park.has_corp_without_vat_contract,
                  park.update_info.revision, park.update_info.last_modified);
}

bool EqualCachedParks(
    const parks_activation::models::CachedParks& cached_parks1,
    const parks_activation::models::CachedParks& cached_parks2) {
  if (cached_parks1.Size() != cached_parks2.Size()) return false;

  if (cached_parks1.Count() != cached_parks2.Count()) return false;

  if (cached_parks1.Cursor() != cached_parks2.Cursor()) return false;

  auto revisions1 = cached_parks1.GetMissedRevisions();
  auto revisions2 = cached_parks2.GetMissedRevisions();

  if (revisions1 != revisions2) return false;

  auto items1 = cached_parks1.FetchAll();
  auto items2 = cached_parks2.FetchAll();

  for (const auto& item1 : items1) {
    const auto item2 = items2.find(item1.first);
    if (item2 == items2.end()) return false;

    if (ToTie(*item1.second) != ToTie(*item2->second)) return false;
  }

  return true;
}

}  // namespace

UTEST_MT(TestDump, TestDumpStoreInterval, 2) {
  auto dumper = CreateDumper();

  auto tp1 = utils::datetime::Stringtime("2019-10-24 12:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp2 = utils::datetime::Stringtime("2019-10-24 12:00:02", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp3 = utils::datetime::Stringtime("2019-10-24 12:00:05", "UTC",
                                         "%Y-%m-%d %H:%M:%S");

  // parks_activation::models::CachedParks cached_parks;
  auto cached_parks = std::make_shared<parks_activation::models::CachedParks>();
  ::utils::datetime::MockNowSet(tp1);
  EXPECT_TRUE(dumper->Store(*cached_parks));
  ::utils::datetime::MockNowSet(tp2);
  EXPECT_FALSE(dumper->Store(*cached_parks));
  ::utils::datetime::MockNowSet(tp3);
  EXPECT_TRUE(dumper->Store(*cached_parks));
}

UTEST_MT(TestDump, TestDumpLoadEmpty, 2) {
  auto cached_parks = std::make_shared<parks_activation::models::CachedParks>();
  auto dumper = CreateDumper();
  EXPECT_FALSE(dumper->Load(*cached_parks));
}

UTEST_MT(TestDump, TestDumpLoadActual, 2) {
  auto dumper = CreateDumper();
  std::chrono::system_clock::time_point tp1 = std::chrono::system_clock::now();
  parks_activation::models::CachedParks cached_parks;
  ::utils::datetime::MockNowSet(tp1);
  EXPECT_TRUE(dumper->Store(cached_parks));
  ::utils::datetime::MockNowSet(tp1 + std::chrono::seconds(5));
  EXPECT_TRUE(dumper->Load(cached_parks));
  ::utils::datetime::MockNowSet(tp1 + kDumpTtlDefault +
                                std::chrono::seconds(1));
  EXPECT_FALSE(dumper->Load(cached_parks));
}

UTEST_MT(TestDump, TestDumpStoreLoadEqual, 2) {
  auto dumper = CreateDumper();

  parks_activation::models::CachedParks cached_parks1;
  parks_activation::models::CachedParks cached_parks2;

  auto ttl = std::chrono::seconds(600);
  auto tp1 = utils::datetime::Stringtime("2019-10-24 12:00:00", "UTC",
                                         "%Y-%m-%d %H:%M:%S");
  auto tp2 = utils::datetime::Stringtime("2019-10-24 12:00:01", "UTC",
                                         "%Y-%m-%d %H:%M:%S");

  auto tp3 = utils::datetime::Stringtime("2019-10-24 12:00:05", "UTC",
                                         "%Y-%m-%d %H:%M:%S");

  ::cache::UpdateStatisticsScopeMock scope(::cache::UpdateType::kFull);

  std::chrono::system_clock::time_point cur_tp =
      std::chrono::system_clock::now();
  ::utils::datetime::MockNowSet(cur_tp);
  cached_parks1.UpsertItems(
      {CreateTestItem(1, tp1), CreateTestItem(4, tp2), CreateTestItem(5, tp3)},
      scope.GetScope(), ttl);
  EXPECT_TRUE(dumper->Store(cached_parks1));
  cur_tp = std::chrono::system_clock::now();
  ::utils::datetime::MockNowSet(std::chrono::system_clock::now() +
                                std::chrono::seconds(5));
  EXPECT_TRUE(dumper->Load(cached_parks2));
  EXPECT_TRUE(EqualCachedParks(cached_parks1, cached_parks2));
}
