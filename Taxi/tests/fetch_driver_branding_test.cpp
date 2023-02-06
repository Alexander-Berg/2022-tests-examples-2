#include <gtest/gtest.h>

#include <clients/driver-profiles/client_mock_base.hpp>
#include <clients/parks/client_mock_base.hpp>

#include <helpers/fetch_info.hpp>

#include "common.hpp"

namespace {

namespace dpc = clients::driver_profiles::
    v1_vehicle_bindings_cars_retrieve_by_driver_id::post;

static const std::string park_id{"park_1"};
static const std::string driver_profile_id{"driver_1"};
static const std::string car_id{"car_1"};

struct CarData {
  std::string park_id;
  std::string car_id;
  std::vector<std::string> amenities;
  bool sticker_confirmed;
  bool lightbox_confirmed;
};

class MockParksClient final : public ::clients::parks::ClientMockBase {
 public:
  MockParksClient(const std::vector<CarData>& data) : data_(data) {}
  clients::parks::cars_list::post::Response CarsList(
      const clients::parks::cars_list::post::Request& /*request*/,
      const clients::parks::CommandControl& /*command_control*/ = {})
      const final {
    clients::parks::cars_list::post::Response result;

    for (const auto& car : data_) {
      clients::parks::Vehicle vehicle;
      vehicle.id = car.car_id;
      vehicle.amenities = car.amenities;
      vehicle.lightbox_confirmed = car.lightbox_confirmed;
      vehicle.sticker_confirmed = car.sticker_confirmed;
      result.cars.push_back(std::move(vehicle));
    }

    return result;
  }

 private:
  const std::vector<CarData> data_;
};

struct DriverData {
  std::string park_id;
  std::string driver_profile_id;
  std::string car_id;
};

class MockDriverProfilesClient
    : public ::clients::driver_profiles::ClientMockBase {
 public:
  MockDriverProfilesClient(const std::vector<DriverData>& data) : data_(data) {}

  dpc::Response GetCarIds(
      const dpc::Request& /*request*/,
      const ::clients::driver_profiles::CommandControl& /*command_control*/
      = {}) const final {
    dpc::Response result;

    for (const auto& data : data_) {
      dpc::Response200ProfilesA profile;

      profile.park_driver_profile_id =
          data.park_id + "_" + data.driver_profile_id;
      if (!data.car_id.empty()) {
        profile.data = dpc::Response200ProfilesAData{data.car_id};
      }
      result.profiles.push_back(std::move(profile));
    }

    return result;
  }

 private:
  std::vector<DriverData> data_;
};

}  // namespace

struct CarBrandingFixture : public ::testing::Test {
 public:
  MockParksClient CreateParksMock(const std::vector<CarData>& data) {
    return MockParksClient(data);
  }
};

struct CarBrandingData {
  std::vector<CarData> data;
  models::Branding expected_branding;
};

struct CarBrandingFixtureParametrized
    : public ::testing::TestWithParam<CarBrandingData> {
 public:
  MockParksClient CreateParksMock() { return MockParksClient(GetParam().data); }
};

TEST_P(CarBrandingFixtureParametrized, Variants) {
  ASSERT_EQ(GetParam().expected_branding,
            helpers::impl::GetCarBranding(park_id, car_id, CreateParksMock()));
}

TEST_F(CarBrandingFixture, InvalidData) {
  ASSERT_THROW(helpers::impl::GetCarBranding(
                   park_id, car_id,
                   CreateParksMock({{"invalid", "data", {}, false, false}})),
               std::runtime_error);
}

struct CarIdData {
  std::vector<DriverData> data;
  std::string expected_car_id;
};

struct CarIdFixture : public ::testing::Test {
 public:
  MockDriverProfilesClient CreateDriverProfilesMock(
      const std::vector<DriverData>& data) {
    return MockDriverProfilesClient(data);
  }
};

struct CarIdFixtureParametrized : public ::testing::TestWithParam<CarIdData> {
 public:
  MockDriverProfilesClient CreateDriverProfilesMock() {
    return MockDriverProfilesClient(GetParam().data);
  }
};

TEST_P(CarIdFixtureParametrized, Variants) {
  ASSERT_EQ(GetParam().expected_car_id,
            helpers::impl::GetCarId(park_id, driver_profile_id,
                                    CreateDriverProfilesMock()));
}

TEST_F(CarIdFixture, InvalidData) {
  ASSERT_THROW(helpers::impl::GetCarId(
                   park_id, driver_profile_id,
                   CreateDriverProfilesMock({{"invalid", "data", ""}})),
               std::runtime_error);

  ASSERT_THROW(helpers::impl::GetCarId(park_id, driver_profile_id,
                                       CreateDriverProfilesMock({})),
               std::runtime_error);
}

struct DriverBrandingFixture : public ::testing::Test {
 public:
  MockParksClient CreateParksMock(const std::vector<CarData>& data) {
    return MockParksClient(data);
  }

  MockDriverProfilesClient CreateDriverProfilesMock(
      const std::vector<DriverData>& data) {
    return MockDriverProfilesClient(data);
  }
};

constexpr models::Branding kNoBranding{false, false};
constexpr models::Branding kSticker{true, false};
constexpr models::Branding kLightbox{false, true};
constexpr models::Branding kFullBranding{true, true};

TEST_F(DriverBrandingFixture, Test) {
  ASSERT_EQ(
      helpers::FetchBranding(
          park_id, driver_profile_id,
          CreateDriverProfilesMock({{park_id, driver_profile_id, car_id}}),
          CreateParksMock({{park_id, car_id, {"sticker"}, true, false}})),
      kSticker);

  ASSERT_EQ(
      helpers::FetchBranding(
          park_id, driver_profile_id,
          CreateDriverProfilesMock({{park_id, driver_profile_id, car_id}}),
          CreateParksMock(
              {{park_id, car_id, {"sticker"}, true, false},
               {park_id, "invalid_car", {"lightbox"}, false, true}})),
      kSticker);

  ASSERT_THROW(helpers::FetchBranding(
                   park_id, driver_profile_id,
                   CreateDriverProfilesMock({{"invalid", "data", ""}}),
                   CreateParksMock({})),
               std::runtime_error);
}

static const std::vector<CarBrandingData> kBrandingVariants{
    {{{park_id, car_id, {}, false, false}}, kNoBranding},
    {{{park_id, car_id, {}, true, false}}, kNoBranding},
    {{{park_id, car_id, {}, false, false}}, kNoBranding},
    {{{park_id, car_id, {}, true, true}}, kNoBranding},

    {{{park_id, car_id, {"trash"}, false, false}}, kNoBranding},
    {{{park_id, car_id, {"trash"}, true, false}}, kNoBranding},
    {{{park_id, car_id, {"trash"}, false, true}}, kNoBranding},
    {{{park_id, car_id, {"trash"}, true, true}}, kNoBranding},

    {{{park_id, car_id, {"sticker"}, false, false}}, kNoBranding},
    {{{park_id, car_id, {"sticker"}, true, false}}, kSticker},
    {{{park_id, car_id, {"sticker"}, false, true}}, kNoBranding},
    {{{park_id, car_id, {"sticker"}, true, true}}, kSticker},

    {{{park_id, car_id, {"lightbox"}, false, false}}, kNoBranding},
    {{{park_id, car_id, {"lightbox"}, true, false}}, kNoBranding},
    {{{park_id, car_id, {"lightbox"}, false, true}}, kLightbox},
    {{{park_id, car_id, {"lightbox"}, true, true}}, kLightbox},

    {{{park_id, car_id, {"sticker", "lightbox"}, false, false}}, kNoBranding},
    {{{park_id, car_id, {"sticker", "lightbox"}, true, false}}, kSticker},
    {{{park_id, car_id, {"sticker", "lightbox"}, false, true}}, kLightbox},
    {{{park_id, car_id, {"sticker", "lightbox"}, true, true}}, kFullBranding},
};

INSTANTIATE_TEST_SUITE_P(CarBranding, CarBrandingFixtureParametrized,
                         ::testing::ValuesIn(kBrandingVariants));

static const std::vector<CarIdData> kIdVariants{
    {{{park_id, driver_profile_id, car_id}}, car_id},
};

INSTANTIATE_TEST_SUITE_P(CarId, CarIdFixtureParametrized,
                         ::testing::ValuesIn(kIdVariants));
