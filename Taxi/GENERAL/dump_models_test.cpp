#include <userver/utest/utest.hpp>

#include <userver/dump/test_helpers.hpp>

#include <models/entity.hpp>
#include <models/entity_type.hpp>
#include <models/match.hpp>

using dump::TestWriteReadCycle;

TEST(CacheDumpModels, Entity) {
  TestWriteReadCycle(models::Entity{models::EntityName{"my_entity_name"},
                                    models::EntityType::kDbidUuid});
}

TEST(CacheDumpModels, Match) {
  TestWriteReadCycle(models::Match{models::TagNameId{1024},
                                   models::ProviderId{12},
                                   std::chrono::system_clock::now()});
}

TEST(CacheDumpModels, MatchInfinity) {
  TestWriteReadCycle(models::Match{models::TagNameId{1024},
                                   models::ProviderId{12}, utils::kInfinity});
}

TEST(CacheDumpModels, EntityType) {
  TestWriteReadCycle(models::EntityType::kDbidUuid);
}

TEST(CacheDumpModels, EntityTypesOrder) {
  using Type = models::EntityType;

  const auto to_dump_value = [](const Type type) -> uint8_t {
    // Important notice:
    //  if you find yourself modifying this test, make sure one of
    //  the following would be accomplished:
    //    1. You add a new value to the end of EntityType enumeration.
    //    2. You modify the enumeration and increase the dump versions
    //      of all caches that use the serialization mechanism
    //      in configs/{unit-name}/config.user.yaml.
    switch (type) {
      case Type::kDriverLicense:
        return 0;
      case Type::kCarNumber:
        return 1;
      case Type::kPark:
        return 2;
      case Type::kUdid:
        return 3;
      case Type::kClidUuid:
        return 4;
      case Type::kPhone:
        return 5;
      case Type::kPhoneHashId:
        return 6;
      case Type::kUserId:
        return 7;
      case Type::kUserPhoneId:
        return 8;
      case Type::kPersonalPhoneId:
        return 9;
      case Type::kDbidUuid:
        return 10;
      case Type::kCorpClientId:
        return 11;
      case Type::kParkCarId:
        return 12;
      case Type::kBrandId:
        return 13;
      case Type::kCategoryId:
        return 14;
      case Type::kPlaceId:
        return 15;
      case Type::kYandexUid:
        return 16;
      case Type::kStoreId:
        return 17;
      case Type::kItemId:
        return 18;
      case Type::kStoreItemId:
        return 19;
    }
  };

  for (const auto type : ::handlers::kEntityTypeValues) {
    const auto value = to_dump_value(type);
    ASSERT_EQ(dump::ToBinary(type), dump::ToBinary(value));
  }
}
