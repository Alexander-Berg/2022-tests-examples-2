#pragma once

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <internal/experiments3_adapter.hpp>

namespace shuttle_control::internal {

class Experiments3AdapterMock
    : public ::shuttle_control::internal::Experiments3Adapter {
 public:
  Experiments3AdapterMock() : Experiments3Adapter(nullptr){};
  MOCK_METHOD(
      experiments3::ShuttleMatchInWorkshift::Value, GetMatchInWorkshift,
      (const std::string& route_name, const ::models::DbidUuid& dbid_uuid,
       const std::optional<::shuttle_control::models::Workshift>& workshift),
      (const, override));
  MOCK_METHOD(experiments3::shuttle_control_stop_restrictions::Value,
              GetStopRestrictions,
              (const std::string& route_name,
               const std::optional<std::string>& yandex_uid,
               const std::optional<std::string>& phone_id,
               const std::optional<std::string>& origin_service_id,
               const std::optional<std::string>& external_passenger_id,
               const std::optional<::models::DbidUuid>& dbid_uuid),
              (const, override));
  MOCK_METHOD(experiments3::ShuttleSlaParams::Value, GetSLAParams,
              (const std::string& route_name,
               const std::optional<::models::DbidUuid>& dbid_uuid,
               const std::optional<std::string>& origin_service_id),
              (const, override));
};

}  // namespace shuttle_control::internal
