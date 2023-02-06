#pragma once

#include <gmock/gmock.h>
#include <models/roles.hpp>
#include <userver/utest/utest.hpp>

namespace testing {

namespace role = ::eats_partners::types::role;
namespace role_template = ::eats_partners::types::role_template;

struct RolesStoragePgMock
    : public ::eats_partners::models::roles::detail::IStorageImpl {
  MOCK_METHOD(std::vector<role::Role>, GetRoles, (), (const, override));
  MOCK_METHOD(std::vector<role::Role>, GetRoleByIds,
              (const std::vector<int>& role_ids), (const, override));
  MOCK_METHOD(std::vector<role_template::RoleTemplate>,
              GetRolesTemplatesBySlugs,
              (const std::vector<std::string>& role_slugs), (const, override));
};

struct RolesStorageMock : public ::eats_partners::models::roles::Storage {
  RolesStorageMock(std::shared_ptr<RolesStoragePgMock> storage_mock)
      : ::eats_partners::models::roles::Storage(storage_mock) {}
  MOCK_METHOD(std::vector<role::Role>, GetRoles, (), (const));
  MOCK_METHOD(std::vector<role::Role>, GetRoleByIds,
              (const std::vector<int>& role_ids), (const));
  MOCK_METHOD(std::vector<role_template::RoleTemplate>,
              GetRolesTemplatesBySlugs,
              (const std::vector<std::string>& role_slugs), (const));
};

}  // namespace testing
