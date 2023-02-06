#include <pricing-components/helpers/data_ids.hpp>

#include <gtest/gtest.h>

namespace helpers::data_ids {

bool operator==(const ParsedId::TransferInfo& lhs,
                const ParsedId::TransferInfo& rhs) {
  return lhs.source_zone == rhs.source_zone &&
         lhs.destination_zone == rhs.destination_zone;
}

bool operator==(const ParsedId& lhs, const ParsedId& rhs) {
  return lhs.object_type == rhs.object_type &&
         lhs.database_id == rhs.database_id &&
         lhs.transfer_info == rhs.transfer_info;
}

}  // namespace helpers::data_ids

TEST(DataIds, ParseId) {
  using helpers::data_ids::BadIdException;
  using helpers::data_ids::ParsedId;
  using helpers::data_ids::ParseId;

  EXPECT_THROW(ParseId("a/a1b2c3d4e"), BadIdException);
  EXPECT_THROW(ParseId("c/a1b2c3d4e//"), BadIdException);
  EXPECT_THROW(ParseId("g/"), BadIdException);
  EXPECT_THROW(ParseId("c/a1b2c3d4e/"), BadIdException);
  EXPECT_THROW(ParseId("c/a1b2c3d4e/aaa"), BadIdException);
  EXPECT_THROW(ParseId("g/a1b2c3d4e/aaa/bbb"), BadIdException);
  EXPECT_THROW(ParseId("d/a1b2c3d4e/aaa/bbb"), BadIdException);
  EXPECT_THROW(ParseId("d/a1b2c3d4e"), BadIdException);

  EXPECT_EQ(ParseId("c/a1b2c3d4e/aaa/bbb"),
            (ParsedId{ParsedId::ObjectType::kCategoryPrices, "a1b2c3d4e",
                      ParsedId::TransferInfo{"aaa", "bbb"}, std::nullopt}));
  EXPECT_EQ(ParseId("g/a1b2c3d4e"),
            (ParsedId{ParsedId::ObjectType::kGeoarea, "a1b2c3d4e", std::nullopt,
                      std::nullopt}));
  EXPECT_EQ(ParseId("c/a1b2c3d4e"),
            (ParsedId{ParsedId::ObjectType::kCategoryPrices, "a1b2c3d4e",
                      std::nullopt, std::nullopt}));
  EXPECT_EQ(ParseId("d/a1b2c3d4e/ttt"),
            (ParsedId{ParsedId::ObjectType::kDecoupling, "ttt", std::nullopt,
                      std::optional<std::string>("a1b2c3d4e")}));
  EXPECT_EQ(ParseId("d/a1b2c3d4e/ttt/aaa/bbb"),
            (ParsedId{ParsedId::ObjectType::kDecoupling, "ttt",
                      ParsedId::TransferInfo{"aaa", "bbb"},
                      std::optional<std::string>("a1b2c3d4e")}));
  EXPECT_EQ(ParseId("c/99b2095ba079490e94c4dab135fdee5a/kamensk-shakhtinsky/"
                    "staraya_stanitsa"),
            (ParsedId{ParsedId::ObjectType::kCategoryPrices,
                      "99b2095ba079490e94c4dab135fdee5a",
                      ParsedId::TransferInfo{"kamensk-shakhtinsky",
                                             "staraya_stanitsa"},
                      std::nullopt}));
  EXPECT_EQ(
      ParseId(
          "c/cfc0bb77b3da4f21a1698adc12d3e3ba/naryan-mar_airport/naryan-mar"),
      (ParsedId{ParsedId::ObjectType::kCategoryPrices,
                "cfc0bb77b3da4f21a1698adc12d3e3ba",
                ParsedId::TransferInfo{"naryan-mar_airport", "naryan-mar"},
                std::nullopt}));
}
