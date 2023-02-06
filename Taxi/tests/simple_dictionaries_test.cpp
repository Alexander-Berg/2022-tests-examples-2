#include "dictionaries/simple_dictionaries.hpp"

#include <userver/utest/utest.hpp>

namespace {

namespace eats_dict = eats_nomenclature::dictionaries;
namespace eats_mods = eats_nomenclature::models;

struct DictData {
  std::unordered_map<eats_mods::MeasureUnitValue, eats_mods::MeasureUnitId>
      measure_units;
  std::unordered_map<eats_mods::BarcodeTypeValue, eats_mods::BarcodeTypeId>
      barcode_types;
  std::unordered_map<eats_mods::BarcodeWeightEncodingValue,
                     eats_mods::BarcodeWeightEncodingId>
      barcode_weight_encodings;
  std::unordered_map<eats_mods::VolumeUnitValue, eats_mods::VolumeUnitId>
      volume_units;
  std::unordered_map<eats_mods::ShippingTypeValue, eats_mods::ShippingTypeId>
      shipping_types;
};

class SimpleDictionariesTest : public ::testing::Test {
 public:
  SimpleDictionariesTest() = default;

 protected:
  void InitializeDictionaries(const DictData& data) {
    auto data_copy = data;
    dicts_ = std::make_unique<eats_dict::SimpleDictionaries>(
        std::move(data_copy.measure_units), std::move(data_copy.barcode_types),
        std::move(data_copy.barcode_weight_encodings),
        std::move(data_copy.volume_units), std::move(data_copy.shipping_types));
  }

 protected:
  std::unique_ptr<eats_dict::SimpleDictionaries> dicts_;
};

}  // namespace

namespace eats_nomenclature::partners::processing::tests {

TEST_F(SimpleDictionariesTest, Find_CaseInsensitive) {
  const std::string test_string = "String";
  const int test_value = 1;

  ::DictData data;
  data.measure_units.try_emplace(models::MeasureUnitValue{test_string},
                                 test_value);
  data.barcode_types.try_emplace(models::BarcodeTypeValue{test_string},
                                 test_value);
  data.barcode_weight_encodings.try_emplace(
      models::BarcodeWeightEncodingValue{test_string}, test_value);
  data.volume_units.try_emplace(models::VolumeUnitValue{test_string},
                                test_value);
  data.shipping_types.try_emplace(models::ShippingTypeValue{test_string},
                                  test_value);

  InitializeDictionaries(data);

  const std::string test_cased_string = "StRiNg";

  {
    const auto value_opt =
        dicts_->FindMeasureUnit(models::MeasureUnitValue{test_string});
    const auto value_opt_2 =
        dicts_->FindMeasureUnit(models::MeasureUnitValue{test_cased_string});
    ASSERT_EQ(value_opt, value_opt_2);
  }
  {
    const auto value_opt =
        dicts_->FindBarcodeType(models::BarcodeTypeValue{test_string});
    const auto value_opt_2 =
        dicts_->FindBarcodeType(models::BarcodeTypeValue{test_cased_string});
    ASSERT_EQ(value_opt, value_opt_2);
  }
  {
    const auto value_opt = dicts_->FindBarcodeWeightEncoding(
        models::BarcodeWeightEncodingValue{test_string});
    const auto value_opt_2 = dicts_->FindBarcodeWeightEncoding(
        models::BarcodeWeightEncodingValue{test_cased_string});
    ASSERT_EQ(value_opt, value_opt_2);
  }
  {
    const auto value_opt =
        dicts_->FindVolumeUnit(models::VolumeUnitValue{test_string});
    const auto value_opt_2 =
        dicts_->FindVolumeUnit(models::VolumeUnitValue{test_cased_string});
    ASSERT_EQ(value_opt, value_opt_2);
  }
  {
    const auto value_opt =
        dicts_->FindShippingType(models::ShippingTypeValue{test_string});
    const auto value_opt_2 =
        dicts_->FindShippingType(models::ShippingTypeValue{test_cased_string});
    ASSERT_EQ(value_opt, value_opt_2);
  }
}

}  // namespace eats_nomenclature::partners::processing::tests
