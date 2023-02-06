#include <userver/utest/utest.hpp>

#include <candidates/processors/dummy/dummy.hpp>
#include <candidates/result_storages/dummy/dummy.hpp>
#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>
#include "driver_ids.hpp"

namespace {

namespace json = formats::json;

candidates::Environment CreateEnvironment() {
  return candidates::Environment(dynamic_config::GetDefaultSnapshot());
}

}  // namespace

UTEST(DriverIdsGeoIndex, Empty) {
  const auto& positions = std::make_shared<const models::DriverPositions>();
  candidates::geoindexes::DriverIds geoindex(positions);

  candidates::result_storages::Dummy storage;
  candidates::processors::Dummy processor(storage);
  formats::json::Value params;
  const auto& env = CreateEnvironment();
  EXPECT_THROW(geoindex.Search(params, env, processor),
               formats::json::Exception);
  EXPECT_EQ(processor.size(), 0);

  json::ValueBuilder builder;
  builder[candidates::geoindexes::DriverIds::kDriverIds] =
      json::ValueBuilder(json::Type::kArray);
  params = builder.ExtractValue();
  EXPECT_NO_THROW(geoindex.Search(params, env, processor));
  EXPECT_EQ(processor.size(), 0);
}

UTEST(DriverIdsGeoIndex, NonEmpty) {
  models::DriverPositions positions;
  models::TrackPointEx point;
  point.lon = point.lat = 1;
  positions.emplace("dbid1_uuid1", point);
  point.lon = point.lat = 2;
  positions.emplace("dbid1_uuid2", point);
  candidates::geoindexes::DriverIds geoindex(
      std::make_shared<const models::DriverPositions>(std::move(positions)));

  candidates::result_storages::Dummy storage;
  candidates::processors::Dummy processor(storage);
  json::ValueBuilder ids(json::Type::kArray);
  ids.PushBack("dbid1_uuid1");
  ids.PushBack("dbid1_uuid2");
  json::ValueBuilder id_obj(json::Type::kObject);
  id_obj["dbid"] = "dbid1";
  id_obj["uuid"] = "uuid3";
  ids.PushBack(id_obj.ExtractValue());
  json::ValueBuilder params;
  const auto& env = CreateEnvironment();
  params[candidates::geoindexes::DriverIds::kDriverIds] = std::move(ids);
  EXPECT_NO_THROW(geoindex.Search(params.ExtractValue(), env, processor));
  ASSERT_EQ(processor.size(), 3);
  const auto& result = storage.Get();
  EXPECT_EQ(result[0].member.id, "dbid1_uuid1");
  EXPECT_EQ(result[0].member.position.lon, 1);
  EXPECT_EQ(result[1].member.id, "dbid1_uuid2");
  EXPECT_EQ(result[1].member.position.lon, 2);
  EXPECT_EQ(result[2].member.id, "dbid1_uuid3");
}
