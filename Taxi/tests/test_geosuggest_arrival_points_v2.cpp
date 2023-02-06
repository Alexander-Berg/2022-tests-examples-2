#include <gtest/gtest.h>

#include <flatbuffers/flatbuffers.h>

#include <ml/common/filesystem.hpp>
#include <ml/geosuggest/arrival_points/v2/fb_objects.hpp>
#include <ml/geosuggest/arrival_points/v2/resource.hpp>

#include "common/utils.hpp"

namespace {
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("geosuggest_arrival_points_v2");
}  // namespace

namespace arrival_points = ml::geosuggest::arrival_points::v2;

TEST(ArrivalPointsV2, points_storage_from_flatbuffer) {
  const arrival_points::Resource resource{kTestDataDir + "/resource", true};
  const auto& storage = resource.GetArrivalPointsStorage();
  ASSERT_EQ(storage->addresses.size(), 2ul);
}

TEST(ArrivalPointsV2, points_storage_adding_elements) {
  flatbuffers::FlatBufferBuilder builder;

  // build vector of ArrivalPoint objects
  auto id = builder.CreateString("id");
  arrival_points::ArrivalPointFbBuilder arrival_point_builder{builder};
  arrival_point_builder.add_id(id);
  auto geopoint = arrival_points::GeoPointFb{34, 56};
  arrival_point_builder.add_position(&geopoint);
  arrival_point_builder.add_popularity(10);
  auto arrival_point = arrival_point_builder.Finish();
  flatbuffers::Offset<arrival_points::ArrivalPointFb> candidates_vec[1];
  candidates_vec[0] = arrival_point;

  // build vector of Address objects
  auto uri = builder.CreateString("uri");
  auto address_id = builder.CreateString("id");
  auto candidates = builder.CreateVectorOfSortedTables(candidates_vec, 1);
  arrival_points::AddressFbBuilder address_builder{builder};
  address_builder.add_uri(uri);
  address_builder.add_id(address_id);
  address_builder.add_candidates(candidates);
  address_builder.add_popularity(0.6);
  auto address = address_builder.Finish();
  flatbuffers::Offset<arrival_points::AddressFb> addresses_vec[1];
  addresses_vec[0] = address;

  // build ArrivalPointsStorage
  auto addressed_vector = builder.CreateVectorOfSortedTables(addresses_vec, 1);
  arrival_points::ArrivalPointsStorageFbBuilder points_storage_builder{builder};
  points_storage_builder.add_addresses(addressed_vector);
  auto points_storage_buf = points_storage_builder.Finish();
  arrival_points::FinishArrivalPointsStorageFbBuffer(builder,
                                                     points_storage_buf);

  const auto def_obj = builder.GetBufferPointer();
  const auto points_storage =
      arrival_points::GetArrivalPointsStorageFb(def_obj);
  const auto addresses = points_storage->addresses();
  const auto address_in_storage = addresses->LookupByKey("uri");
  ASSERT_NE(addresses, nullptr);
  ASSERT_EQ(addresses->size(), 1ul);
  ASSERT_EQ(address_in_storage->popularity(), 0.6);
  ASSERT_EQ(address_in_storage->candidates()->size(), 1ul);
  ASSERT_EQ(address_in_storage->candidates()->Get(0)->popularity(), 10);
}
