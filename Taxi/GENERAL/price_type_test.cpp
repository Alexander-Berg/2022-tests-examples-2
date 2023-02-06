#include <gtest/gtest.h>

#include <unordered_set>

#include <pricing-extended/models/price_type.hpp>

namespace models {
class PriceTypeFlagsTest : public PriceTypeFlags {
 public:
  explicit PriceTypeFlagsTest(const PriceTypeFlags& other)
      : PriceTypeFlags(other) {}

  operator uint16_t() const { return static_cast<uint16_t>(value_.to_ulong()); }
};
}  // namespace models

namespace {
using models::PriceTypeFlags;

const PriceTypeFlags kOnlyStrikeout{PriceTypeFlags{} |
                                    PriceTypeFlags::kStrikeout};

const PriceTypeFlags kAllWithoutStrikeout{
    PriceTypeFlags{} | PriceTypeFlags::kTotal | PriceTypeFlags::kAntisurge |
    PriceTypeFlags::kPaidSupply | PriceTypeFlags::kPlusPromo |
    PriceTypeFlags::kComboOrder | PriceTypeFlags::kComboInner |
    PriceTypeFlags::kComboOuter};

const PriceTypeFlags kAllWithStrikeout{kAllWithoutStrikeout | kOnlyStrikeout};

}  // namespace

class PriceTypeValidator
    : public ::testing::TestWithParam<std::tuple<PriceTypeFlags, uint16_t>> {};

TEST_P(PriceTypeValidator, PriceTypeValidator) {
  const auto& [actual, expected] = GetParam();
  EXPECT_EQ(static_cast<uint16_t>(models::PriceTypeFlagsTest(actual)),
            expected);
}

INSTANTIATE_TEST_SUITE_P(
    PriceTypeValidator, PriceTypeValidator,
    ::testing::Values(  //
        std::make_tuple<PriceTypeFlags, uint16_t>(PriceTypeFlags{}, 0x0000),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kOnlyStrikeout}, 0x8000),
        std::make_tuple<PriceTypeFlags, uint16_t>(PriceTypeFlags::kTotal,
                                                  0x0001),
        std::make_tuple<PriceTypeFlags, uint16_t>(PriceTypeFlags::kAntisurge,
                                                  0x0002),
        std::make_tuple<PriceTypeFlags, uint16_t>(PriceTypeFlags::kPaidSupply,
                                                  0x0004),
        std::make_tuple<PriceTypeFlags, uint16_t>(PriceTypeFlags::kPlusPromo,
                                                  0x0008),
        std::make_tuple<PriceTypeFlags, uint16_t>(PriceTypeFlags::kComboOrder,
                                                  0x0010),
        std::make_tuple<PriceTypeFlags, uint16_t>(PriceTypeFlags::kComboInner,
                                                  0x0020),
        std::make_tuple<PriceTypeFlags, uint16_t>(PriceTypeFlags::kComboOuter,
                                                  0x0040),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithoutStrikeout}, 0x007f),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout}, 0x807f),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{PriceTypeFlags::kTotal} | PriceTypeFlags::kStrikeout,
            0x8001),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{PriceTypeFlags::kAntisurge} |
                PriceTypeFlags::kStrikeout,
            0x8002),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{PriceTypeFlags::kPaidSupply} |
                PriceTypeFlags::kStrikeout,
            0x8004),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{PriceTypeFlags::kPlusPromo} |
                PriceTypeFlags::kStrikeout,
            0x8008),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{PriceTypeFlags::kComboOrder} |
                PriceTypeFlags::kStrikeout,
            0x8010),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{PriceTypeFlags::kComboInner} |
                PriceTypeFlags::kStrikeout,
            0x8020),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{PriceTypeFlags::kComboOuter} |
                PriceTypeFlags::kStrikeout,
            0x8040),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} & PriceTypeFlags::kStrikeout,
            0x8000),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} & PriceTypeFlags::kTotal, 0x0001),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} & PriceTypeFlags::kAntisurge,
            0x0002),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} & PriceTypeFlags::kPaidSupply,
            0x0004),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} & PriceTypeFlags::kPlusPromo,
            0x0008),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} & PriceTypeFlags::kComboOrder,
            0x0010),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} & PriceTypeFlags::kComboInner,
            0x0020),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} & PriceTypeFlags::kComboOuter,
            0x0040),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} &
                PriceTypeFlags{kAllWithoutStrikeout},
            0x007f),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} ^
                PriceTypeFlags{kAllWithoutStrikeout},
            0x8000),
        std::make_tuple<PriceTypeFlags, uint16_t>(
            PriceTypeFlags{kAllWithStrikeout} ^ PriceTypeFlags::kStrikeout,
            0x007f)));

TEST(PriceTypeFlags, EachPriceTypeAndStrikeout) {
  for (const auto& type : models::kPriceTypes) {
    for (const auto& strikeout : std::vector{false, true}) {
      PriceTypeFlags flags{type};
      if (strikeout) flags |= PriceTypeFlags::kStrikeout;
      EXPECT_TRUE((flags & type) == type);
      EXPECT_EQ(static_cast<bool>(models::PriceTypeFlagsTest(
                    flags & PriceTypeFlags::kStrikeout)),
                strikeout);
    }
  }
}

TEST(PriceTypeFlags, SplitToSimples) {
  {
    const auto simples = kAllWithoutStrikeout.Split();
    const std::unordered_set<PriceTypeFlags> simples_hash(simples.begin(),
                                                          simples.end());
    EXPECT_EQ(simples.size(), 7);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kTotal), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kAntisurge), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPaidSupply), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPlusPromo), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOrder), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboInner), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOuter), 1);
  }
  {
    const auto simples =
        (kAllWithoutStrikeout ^ PriceTypeFlags::kAntisurge).Split();
    const std::unordered_set<PriceTypeFlags> simples_hash(simples.begin(),
                                                          simples.end());
    EXPECT_EQ(simples.size(), 6);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kTotal), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kAntisurge), 0);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPaidSupply), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPaidSupply), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOrder), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboInner), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOuter), 1);
  }
  {
    const auto simples = kAllWithStrikeout.Split();
    const std::unordered_set<PriceTypeFlags> simples_hash(simples.begin(),
                                                          simples.end());
    EXPECT_EQ(simples.size(), 14);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kTotal), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kAntisurge), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPaidSupply), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPlusPromo), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOrder), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboInner), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOuter), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kTotal} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kAntisurge} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kPaidSupply} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kPlusPromo} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kComboOrder} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kComboInner} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kComboOuter} |
                                 PriceTypeFlags::kStrikeout),
              1);
  }
  {
    const auto simples = (kAllWithStrikeout ^ PriceTypeFlags::kTotal).Split();
    const std::unordered_set<PriceTypeFlags> simples_hash(simples.begin(),
                                                          simples.end());
    EXPECT_EQ(simples.size(), 12);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kTotal), 0);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kAntisurge), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPaidSupply), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPlusPromo), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOrder), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboInner), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOuter), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kTotal} |
                                 PriceTypeFlags::kStrikeout),
              0);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kAntisurge} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kPaidSupply} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kPlusPromo} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kComboOrder} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kComboInner} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kComboOuter} |
                                 PriceTypeFlags::kStrikeout),
              1);
  }
  {
    const auto simples = (kAllWithStrikeout ^ PriceTypeFlags::kTotal ^
                          PriceTypeFlags::kAntisurge)
                             .Split();
    const std::unordered_set<PriceTypeFlags> simples_hash(simples.begin(),
                                                          simples.end());
    EXPECT_EQ(simples.size(), 10);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kTotal), 0);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kAntisurge), 0);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPaidSupply), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kPlusPromo), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOrder), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboInner), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags::kComboOuter), 1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kTotal} |
                                 PriceTypeFlags::kStrikeout),
              0);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kAntisurge} |
                                 PriceTypeFlags::kStrikeout),
              0);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kPaidSupply} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kPlusPromo} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kComboOrder} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kComboInner} |
                                 PriceTypeFlags::kStrikeout),
              1);
    EXPECT_EQ(simples_hash.count(PriceTypeFlags{PriceTypeFlags::kComboOuter} |
                                 PriceTypeFlags::kStrikeout),
              1);
  }
  {
    const auto simples =
        (kAllWithStrikeout ^ PriceTypeFlags::kTotal ^
         PriceTypeFlags::kAntisurge ^ PriceTypeFlags::kPaidSupply ^
         PriceTypeFlags::kPlusPromo ^ PriceTypeFlags::kComboOrder ^
         PriceTypeFlags::kComboInner ^ PriceTypeFlags::kComboOuter)
            .Split();
    const std::unordered_set<PriceTypeFlags> simples_hash(simples.begin(),
                                                          simples.end());
    EXPECT_EQ(simples.size(), 0);
  }
}
