#include <gmock/gmock.h>

#include <models/order.hpp>
#include <tracked_order/car_info_builder.hpp>

namespace {
using handlers::TrackedOrderCarPlatePart;
using handlers::TrackedOrderCarPlatePartType;

using TrackedOrderCarPlateParts = std::vector<TrackedOrderCarPlatePart>;

void TestCarPlateParts(
    const std::string& country_code, const std::string& car_number,
    const std::optional<TrackedOrderCarPlateParts>& expected_parts) {
  const std::optional<TrackedOrderCarPlateParts> result =
      eats_orders_tracking::tracked_order::impl::BuildCarPlates(country_code,
                                                                car_number);

  ASSERT_EQ(result.has_value(), expected_parts.has_value());
  if (!result.has_value()) return;

  ASSERT_THAT(*result, testing::ElementsAreArray(*expected_parts));
}

}  // namespace

TEST(CarNumberParser, RuDefaultEnglish) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kLetter, "A"},
      {TrackedOrderCarPlatePartType::kNumber, "123"},
      {TrackedOrderCarPlatePartType::kLetter, "BC"},
      {TrackedOrderCarPlatePartType::kRegion, "999"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "A123BC999",
                    expected_parts);
}

TEST(CarNumberParser, RuDefaultCyrillic2) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kLetter, "Ы"},
      {TrackedOrderCarPlatePartType::kNumber, "123"},
      {TrackedOrderCarPlatePartType::kLetter, "ЖЙ"},
      {TrackedOrderCarPlatePartType::kRegion, "88"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "Ы123ЖЙ88",
                    expected_parts);
}

TEST(CarNumberParser, RuDefaultCyrillic3) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kLetter, "Ё"},
      {TrackedOrderCarPlatePartType::kNumber, "734"},
      {TrackedOrderCarPlatePartType::kLetter, "МН"},
      {TrackedOrderCarPlatePartType::kRegion, "361"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "Ё734МН361",
                    expected_parts);
}

TEST(CarNumberParser, RuDefaultWithRus) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kLetter, "Ё"},
      {TrackedOrderCarPlatePartType::kNumber, "734"},
      {TrackedOrderCarPlatePartType::kLetter, "МН"},
      {TrackedOrderCarPlatePartType::kRegion, "361"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu,
                    "Ё734МН361РУС", expected_parts);
}

TEST(CarNumberParser, RuDefaultWithoutRegion) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kLetter, "Ё"},
      {TrackedOrderCarPlatePartType::kNumber, "734"},
      {TrackedOrderCarPlatePartType::kLetter, "МН"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "Ё734МН",
                    expected_parts);
}

TEST(CarNumberParser, RuTaxiCyrillic2) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kLetter, "ЖШ"},
      {TrackedOrderCarPlatePartType::kNumber, "888"},
      {TrackedOrderCarPlatePartType::kRegion, "22"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "ЖШ88822",
                    expected_parts);
}

TEST(CarNumberParser, RuTaxiCyrillic3) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kLetter, "ЖШ"},
      {TrackedOrderCarPlatePartType::kNumber, "888"},
      {TrackedOrderCarPlatePartType::kRegion, "333"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "ЖШ888333",
                    expected_parts);
}

TEST(CarNumberParser, RuTaxiWithRus) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kLetter, "ЖШ"},
      {TrackedOrderCarPlatePartType::kNumber, "888"},
      {TrackedOrderCarPlatePartType::kRegion, "333"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "ЖШ888333РУС",
                    expected_parts);
}

TEST(CarNumberParser, RuTaxiWithoutRegion) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kLetter, "ЖШ"},
      {TrackedOrderCarPlatePartType::kNumber, "888"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "ЖШ888",
                    expected_parts);
}

TEST(CarNumberParser, KzEnglish2) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kNumber, "888"},
      {TrackedOrderCarPlatePartType::kLetter, "AB"},
      {TrackedOrderCarPlatePartType::kRegion, "22"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "888AB22",
                    expected_parts);
}

TEST(CarNumberParser, KzEnglish3) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kNumber, "888"},
      {TrackedOrderCarPlatePartType::kLetter, "ABC"},
      {TrackedOrderCarPlatePartType::kRegion, "22"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "888ABC22",
                    expected_parts);
}

TEST(CarNumberParser, ByDefaultEnglish) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kNumber, "0123"},
      {TrackedOrderCarPlatePartType::kNumber, "QQ-7"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeBy, "0123QQ-7",
                    expected_parts);
}

TEST(CarNumberParser, ByDefaultUnicode) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kNumber, "0123"},
      {TrackedOrderCarPlatePartType::kNumber, "ІЎ-7"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeBy, "0123ІЎ-7",
                    expected_parts);
}

TEST(CarNumberParser, ByTaxiEnglish) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kNumber, "7"},
      {TrackedOrderCarPlatePartType::kNumber, "TAX"},
      {TrackedOrderCarPlatePartType::kNumber, "1234"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeBy, "7TAX1234",
                    expected_parts);
}

TEST(CarNumberParser, ByTaxiUnicode) {
  const TrackedOrderCarPlateParts expected_parts = {
      {TrackedOrderCarPlatePartType::kNumber, "7"},
      {TrackedOrderCarPlatePartType::kNumber, "ЖЎІ"},
      {TrackedOrderCarPlatePartType::kNumber, "1234"},
  };
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeBy, "7ЖЎІ1234",
                    expected_parts);
}

TEST(CarNumberParser, InvalidRuFirstLetter0) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "123BC999",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuFirstLetter2) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "AA123BC999",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuNumber2) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "A12BC999",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuNumber4) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "A1234BC999",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuSecondLetter1) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "A123B999",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuSecondLetter3) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "A123BCD999",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuRegion1) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "A123BC9",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuRegion4) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "A123BC9999",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuPrefix) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "1A123BC999Z",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuSuffix) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "A123BC999Z",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuTaxiLetter1) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "A88822",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuTaxiLetter3) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "ABC88822",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuTaxiDigits4) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "AB4444",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidRuTaxiDigits7) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeRu, "AB7777777",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidKzNumber2) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "88AB22",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidKzNumber4) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "8888AB22",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidKzLetter1) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "888A22",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidKzLetter4) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "888ABCD22",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidKzRegion1) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "888AB2",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidKzRegion3) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "888AB222",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidKzPrefix) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "P888AB22",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidKzSuffix) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeKz, "888AB22S",
                    std::nullopt);
}

TEST(CarNumberParser, InvalidBy) {
  TestCarPlateParts(eats_orders_tracking::models::kCountryCodeBy, "x000xx199",
                    std::nullopt);
}
