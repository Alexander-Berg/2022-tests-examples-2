#include "qc_classes_filter.hpp"

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <filters/partners/fetch_qc_classes/utils/common.hpp>
#include <models/classes.hpp>

namespace tests {

namespace {
void CheckFilter(const models::qc::QcClassesFilter& filter,
                 const models::qc::Blocks& blocks,
                 const models::Classes& expected) {
  EXPECT_EQ(filter.GetBlockedClasses(blocks), expected);

  const auto& result = filter.GetBlockedClassesWithDescription(blocks);
  models::Classes blocked;
  for (const auto& [cls, blocks] : result) {
    blocked.Add(cls);
    EXPECT_EQ(blocks, blocks);
  }
  EXPECT_EQ(blocked, expected);
}
}  // namespace

UTEST(QcClasses, DkkTariffs) {
  const auto storage = dynamic_config::MakeDefaultStorage(
      {{configs::qc::kQcClassConfig,
        utils::LoadJson("qc_tariffs_settings_simple.json")}});

  const auto kDkk = models::qc::ExamMapper::Parse("dkk");
  const auto kOrdersOffBlocks =
      utils::MakeBlocks(kDkk, models::qc::SanctionMapper::Parse("orders_off"));
  const auto kDkkComfortOffBlocks = utils::MakeBlocks(
      kDkk, models::qc::SanctionMapper::Parse("dkk_comfort_off"));
  const models::Classes allowed_classes(
      {"delivery", "econom", "comfort", "comfortplus", "business"});

  models::qc::QcClassesFilter filter1(storage.GetSnapshot(), "moscow", "rus",
                                      allowed_classes);
  CheckFilter(
      filter1, kOrdersOffBlocks,
      models::Classes({"econom", "comfort", "comfortplus", "business"}));
  CheckFilter(filter1, kDkkComfortOffBlocks,
              models::Classes({"comfort", "comfortplus", "business"}));

  models::qc::QcClassesFilter filter2(storage.GetSnapshot(), "spb", "rus",
                                      allowed_classes);
  CheckFilter(filter2, kOrdersOffBlocks,
              models::Classes({"econom", "comfort", "comfortplus"}));
  CheckFilter(filter2, kDkkComfortOffBlocks, models::Classes());

  models::qc::QcClassesFilter filter3(storage.GetSnapshot(), "minsk", "blr",
                                      allowed_classes);
  CheckFilter(filter3, kOrdersOffBlocks, models::Classes());
  CheckFilter(filter3, kDkkComfortOffBlocks, models::Classes());
}

}  // namespace tests
