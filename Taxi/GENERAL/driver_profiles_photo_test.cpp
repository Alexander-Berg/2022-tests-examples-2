#include <gtest/gtest.h>

#include <models/parks/driver_profiles/driver_photos.hpp>
#include <utils/json_serializers.hpp>

namespace models {
namespace parks {
namespace driver_profiles {

namespace {

Json::Value MakePhoto(std::string const& scale, std::string const& type) {
  Json::Value photo(Json::objectValue);
  photo["scale"] = scale;
  photo["type"] = type;
  photo["href"] = scale + type;

  return photo;
}

Json::Value AllCombiantions() {
  Json::Value photos(Json::objectValue);
  photos["photos"] = Json::Value(Json::arrayValue);

  for (const auto scale : {"original", "large", "small"})
    for (const auto type : {"driver", "left", "front", "salon"})
      photos["photos"].append(MakePhoto(scale, type));

  return photos;
}

}  // namespace

TEST(DriverPhotos, Serialization) {
  Json::Value expected = AllCombiantions();
  Photos cpp_photos;
  serializers::Deserialize<Photos>(expected, &cpp_photos);
  Json::Value actual;
  serializers::Serialize(cpp_photos, &actual);
  ASSERT_EQ(0, expected.compare(actual));
}

}  // namespace driver_profiles
}  // namespace parks
}  // namespace models
