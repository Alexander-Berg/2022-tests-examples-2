#include <userver/utest/utest.hpp>

#include <boost/range/adaptor/map.hpp>

#include <pricing-components/utils/as.hpp>
#include <utils/matchers.hpp>

namespace {

std::shared_ptr<models::Transfer> MakeTransfer(const std::string& src,
                                               const std::string& dst) {
  auto result = std::make_shared<models::Transfer>();
  result->source_zone = src;
  result->destination_zone = dst;
  result->route_without_jams = false;
  return result;
}

const std::string kInside{"inside"};
const std::string kOutside{"outside"};
const std::string kAway{"away"};
const std::string kSuburb{"suburb"};

const models::Category kInsideCategory{
    price_calc::models::CategoryPrices{0,
                                       0,
                                       {},
                                       {{kInside, {}}, {kSuburb, {}}},
                                       {},
                                       std::nullopt,
                                       std::nullopt,
                                       std::nullopt},
    {},
    "cid1",
    "inside_category",
    "currency",
    {MakeTransfer(kInside, kOutside), MakeTransfer(kInside, kSuburb),
     MakeTransfer(kSuburb, kInside)}};

const models::Category kOutsideCategory{
    price_calc::models::CategoryPrices{
        0,
        0,
        {},
        {{kInside, {}}, {kOutside, {}}, {kSuburb, {}}},
        {},
        std::nullopt,
        std::nullopt,
        std::nullopt},
    {},
    "cid2",
    "outside_category",
    "currency",
    {MakeTransfer(kOutside, kInside), MakeTransfer(kOutside, kSuburb),
     MakeTransfer(kSuburb, kOutside), MakeTransfer(kInside, kSuburb),
     MakeTransfer(kOutside, kAway)}};

const price_calc::models::Polygon kInsidePolygon{{{29.75, 59.75},
                                                  {29.75, 60.25},
                                                  {30.25, 60.25},
                                                  {30.25, 59.75},
                                                  {29.75, 59.75}},
                                                 0.04};

const price_calc::models::Polygon kOutsidePolygon{{{29.25, 59.25},
                                                   {29.25, 60.75},
                                                   {30.75, 60.75},
                                                   {30.75, 59.25},
                                                   {29.25, 59.25}},
                                                  0.36};

const price_calc::models::Polygon kAwayPolygon{
    {{0, 0}, {1, 0}, {1, 1}, {0, 1}, {0, 0}}, 1};

const std::unordered_map<std::string, caches::GeoareaWrapper> kGeoareas{
    {kInside, caches::GeoareaWrapper{models::Geoarea{"gid1", kInside,
                                                     kInsidePolygon, false}}},
    {kOutside, caches::GeoareaWrapper{models::Geoarea{"gid2", kOutside,
                                                      kOutsidePolygon, false}}},
    {kAway, caches::GeoareaWrapper{
                models::Geoarea{"gid3", kAway, kAwayPolygon, false}}}};

const models::GeoareaPtr& kInsideGeoarea = kGeoareas.at(kInside).geoarea;
const models::GeoareaPtr& kOutsideGeoarea = kGeoareas.at(kOutside).geoarea;
const models::GeoareaPtr& kAwayGeoarea = kGeoareas.at(kAway).geoarea;

const models::GeoareasMatcher& GetGeoareasMatcher() {
  static const models::GeoareasMatcher kMatcher{kGeoareas};
  return kMatcher;
}

std::unordered_set<std::string> GetGeoareaNames(
    const std::vector<models::GeoareaPtr>& geoareas) {
  std::unordered_set<std::string> result;
  std::transform(geoareas.begin(), geoareas.end(),
                 std::inserter(result, result.begin()),
                 [](const auto& geoarea) { return geoarea->name; });
  return result;
}

const std::unordered_map<std::string, std::vector<models::Point>> kPoints{
    {kInside, {{30.0, 59.9}, {30.0, 60.1}}},
    {kOutside, {{30.0, 59.3}, {30.0, 60.6}}},
    {kAway, {{0.5, 0.5}}},
    {kSuburb, {{30.0, 58.9}, {30.0, 61.1}}}};

}  // namespace

class PolygonsMatcher
    : public ::testing::TestWithParam<
          std::tuple<std::vector<models::Point>, const models::GeoareaPtr>> {};

TEST_P(PolygonsMatcher, PolygonsMatcher) {
  const auto& [points, expected_geoarea] = GetParam();

  for (const auto& point : points) {
    EXPECT_TRUE(expected_geoarea->polygon.Contains(point));
  }
}

INSTANTIATE_TEST_SUITE_P(
    PolygonsMatcher, PolygonsMatcher,
    ::testing::Values(  //
        std::make_tuple(kPoints.at(kInside), kInsideGeoarea),
        std::make_tuple(kPoints.at(kInside), kOutsideGeoarea),
        std::make_tuple(kPoints.at(kOutside), kOutsideGeoarea),
        std::make_tuple(kPoints.at(kAway), kAwayGeoarea)));

class GeoareasMatcher
    : public ::testing::TestWithParam<std::tuple<
          std::vector<models::Point>, std::vector<models::GeoareaPtr>>> {};

TEST_P(GeoareasMatcher, GeoareasMatcher) {
  const auto& [points, expected_geoareas] = GetParam();
  const auto& matcher = GetGeoareasMatcher();

  for (const auto& point : points) {
    const auto& matched = matcher.Match(point);
    EXPECT_EQ(GetGeoareaNames(matched), GetGeoareaNames(expected_geoareas));
  }
}

INSTANTIATE_TEST_SUITE_P(
    GeoareasMatcher, GeoareasMatcher,
    ::testing::Values(  //
        std::make_tuple(kPoints.at(kInside),
                        std::vector{kInsideGeoarea, kOutsideGeoarea}),
        std::make_tuple(kPoints.at(kOutside), std::vector{kOutsideGeoarea}),
        std::make_tuple(kPoints.at(kSuburb), std::vector<models::GeoareaPtr>{}),
        std::make_tuple(kPoints.at(kAway), std::vector{kAwayGeoarea})));

using OptionalTransfer = std::optional<std::pair<std::string, std::string>>;

class TransfersMatcher
    : public ::testing::TestWithParam<std::tuple<
          models::Point, models::Point, models::Category, OptionalTransfer>> {};

UTEST_P(TransfersMatcher, TransfersMatcher) {
  const auto& [point_a, point_b, category, expected_transfer] = GetParam();

  const auto& matched = utils::matchers::MatchTransfer(
      point_a, point_b, category.transfers,
      As<std::unordered_set<std::string>>(category.rides |
                                          boost::adaptors::map_keys),
      GetGeoareasMatcher(), "econom");

  EXPECT_EQ(!matched, !expected_transfer);
  if (matched) {
    EXPECT_EQ(matched->source_zone, expected_transfer->first);
    EXPECT_EQ(matched->destination_zone, expected_transfer->second);
  }
}

INSTANTIATE_UTEST_SUITE_P(
    TransfersMatcher, TransfersMatcher,
    ::testing::Values(
        // ride by inside is transfer inside->outside (kInsideCategory)
        std::make_tuple(kPoints.at(kInside)[0], kPoints.at(kInside)[1],
                        kInsideCategory,
                        std::make_optional(std::make_pair(kInside, kOutside))),

        // ride by inside is transfer outside->inside (kOutsideCategory)
        std::make_tuple(kPoints.at(kInside)[0], kPoints.at(kInside)[1],
                        kOutsideCategory,
                        std::make_optional(std::make_pair(kOutside, kInside))),

        // ride by zone outside is not transfer
        std::make_tuple(kPoints.at(kOutside)[0], kPoints.at(kOutside)[1],
                        kInsideCategory, std::nullopt),
        std::make_tuple(kPoints.at(kOutside)[0], kPoints.at(kOutside)[1],
                        kOutsideCategory, std::nullopt),

        // ride by zone suburb is not transfer
        std::make_tuple(kPoints.at(kSuburb)[0], kPoints.at(kSuburb)[1],
                        kInsideCategory, std::nullopt),
        std::make_tuple(kPoints.at(kSuburb)[0], kPoints.at(kSuburb)[1],
                        kOutsideCategory, std::nullopt),

        // from inside to outside is transfer inside->outside (kInsideCategory)
        std::make_tuple(kPoints.at(kInside)[0], kPoints.at(kOutside)[0],
                        kInsideCategory,
                        std::make_optional(std::make_pair(kInside, kOutside))),

        // from inside to outside is not transfer (kOutsideCategory)
        std::make_tuple(kPoints.at(kInside)[0], kPoints.at(kOutside)[0],
                        kOutsideCategory, std::nullopt),

        // from outside to inside is transfer suburb->inside (kInsideCategory)
        std::make_tuple(kPoints.at(kOutside)[0], kPoints.at(kInside)[0],
                        kInsideCategory,
                        std::make_optional(std::make_pair(kSuburb, kInside))),

        // from outside to inside is transfer outside->inside (kOutsideCategory)
        std::make_tuple(kPoints.at(kOutside)[0], kPoints.at(kInside)[0],
                        kOutsideCategory,
                        std::make_optional(std::make_pair(kOutside, kInside))),

        // from zone to suburb (has transfer)
        std::make_tuple(kPoints.at(kInside)[0], kPoints.at(kSuburb)[0],
                        kInsideCategory,
                        std::make_optional(std::make_pair(kInside, kSuburb))),
        std::make_tuple(kPoints.at(kInside)[0], kPoints.at(kSuburb)[0],
                        kOutsideCategory,
                        std::make_optional(std::make_pair(kInside, kSuburb))),
        std::make_tuple(kPoints.at(kOutside)[0], kPoints.at(kSuburb)[0],
                        kOutsideCategory,
                        std::make_optional(std::make_pair(kOutside, kSuburb))),

        // from outside to suburb, no transfer for kInsideCategory
        std::make_tuple(kPoints.at(kOutside)[0], kPoints.at(kSuburb)[0],
                        kInsideCategory, std::nullopt),

        // from suburb to zone (has transfer)
        std::make_tuple(kPoints.at(kSuburb)[0], kPoints.at(kInside)[0],
                        kInsideCategory,
                        std::make_optional(std::make_pair(kSuburb, kInside))),
        std::make_tuple(kPoints.at(kSuburb)[0], kPoints.at(kInside)[0],
                        kOutsideCategory,
                        std::make_optional(std::make_pair(kSuburb, kOutside))),
        std::make_tuple(kPoints.at(kSuburb)[0], kPoints.at(kOutside)[0],
                        kOutsideCategory,
                        std::make_optional(std::make_pair(kSuburb, kOutside))),

        // from suburb to outside, no transfer for kInsideCategory
        std::make_tuple(kPoints.at(kSuburb)[0], kPoints.at(kOutside)[0],
                        kInsideCategory, std::nullopt),

        // from inside to away is transfer inside->suburb
        std::make_tuple(kPoints.at(kInside)[0], kPoints.at(kAway)[0],
                        kInsideCategory,
                        std::make_optional(std::make_pair(kInside, kSuburb))),
        std::make_tuple(kPoints.at(kInside)[0], kPoints.at(kAway)[0],
                        kOutsideCategory,
                        std::make_optional(std::make_pair(kInside, kSuburb))),

        // from outside to away, no transfer for kInsideCategory
        std::make_tuple(kPoints.at(kOutside)[0], kPoints.at(kAway)[0],
                        kInsideCategory, std::nullopt),

        // from outside to away is transfer outside->away for kOutsideCategory
        std::make_tuple(kPoints.at(kOutside)[0], kPoints.at(kAway)[0],
                        kOutsideCategory,
                        std::make_optional(std::make_pair(kOutside, kAway)))

            ));
