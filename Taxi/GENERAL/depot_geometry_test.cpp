#include <userver/utest/utest.hpp>

#include <models/depot_geometry.hpp>
#include <userver/formats/json/serialize.hpp>

using DepotGeometry = overlord_catalog::models::DepotGeometry;

TEST(DepotGeometryParse, LavkaProspectMira) {
  auto json = formats::json::FromString(R"(
		{
            "coordinates" : [
               [
                  [
                     [
                        37.852672,
                        55.779078
                     ],
                     [
                        37.861792,
                        55.780819
                     ],
                     [
                        37.870154,
                        55.769703
                     ],
                     [
                        37.874535,
                        55.763165
                     ],
                     [
                        37.87634,
                        55.75924
                     ],
                     [
                        37.873615,
                        55.756506
                     ],
                     [
                        37.8678,
                        55.754545
                     ],
                     [
                        37.854469,
                        55.751833
                     ],
                     [
                        37.84736,
                        55.750525
                     ],
                     [
                        37.846446,
                        55.756186
                     ],
                     [
                        37.843159,
                        55.755504
                     ],
                     [
                        37.843623,
                        55.76169
                     ],
                     [
                        37.843736,
                        55.766947
                     ],
                     [
                        37.846488,
                        55.768072
                     ],
                     [
                        37.843612,
                        55.773545
                     ],
                     [
                        37.844094,
                        55.775123
                     ],
                     [
                        37.845656,
                        55.77678
                     ],
                     [
                        37.852672,
                        55.779078
                     ]
                  ]
               ]
            ],
            "type" : "MultiPolygon"
         }
)");

  auto g = Parse(json, formats::parse::To<DepotGeometry>());

  EXPECT_FALSE(g.Contains({}));

  const auto inside =
      geometry::Position(55.76069 * geometry::lat, 37.86147 * geometry::lon);
  EXPECT_TRUE(g.Contains(inside));

  const auto outside =
      geometry::Position(55.74994 * geometry::lat, 37.86872 * geometry::lon);
  EXPECT_FALSE(g.Contains(outside));
}

TEST(DepotGeometryParse, LavkaKamenshiky) {
  auto json = formats::json::FromString(R"(

{
   "coordinates" : [
      [
         [
            [
               37.640106,
               55.736991
            ],
            [
               37.64178,
               55.737675
            ],
            [
               37.642429,
               55.736234
            ],
            [
               37.643936,
               55.736374
            ],
            [
               37.64487,
               55.735532
            ],
            [
               37.642016,
               55.733668
            ],
            [
               37.641038,
               55.735366
            ],
            [
               37.640106,
               55.736991
            ]
         ]
      ]
   ],
   "type" : "MultiPolygon"
}
)");

  auto g = Parse(json, formats::parse::To<DepotGeometry>());

  EXPECT_FALSE(g.Contains({}));

  const auto inside = geometry::Position(55.73450198879418 * geometry::lat,
                                         37.6415095537858 * geometry::lon);
  EXPECT_FALSE(g.Contains(inside));
}
