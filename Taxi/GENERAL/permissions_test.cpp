#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include "permissions.hpp"

namespace helpers::permissions {

TEST(GetMissingPermissions, HasPermissionsOneRole) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& permissions_config =
      config.Get<::taxi_config::TaxiConfig>()
          .eats_restapp_authorizer_roles_permissions_settings;

  std::unordered_set<std::string> roles;
  roles.insert("ROLE_OPERATOR");

  std::vector<std::string> permissions{"permission.orders.active",
                                       "permission.restaurant.menu"};
  const auto missing_permissions =
      GetMissingPermissions(permissions_config, roles, permissions);
  ASSERT_EQ(missing_permissions.size(), 0);
}

TEST(GetMissingPermissions, NoManagmentPermissionOneRole) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& permissions_config =
      config.Get<::taxi_config::TaxiConfig>()
          .eats_restapp_authorizer_roles_permissions_settings;

  std::unordered_set<std::string> roles;
  roles.insert("ROLE_OPERATOR");

  std::vector<std::string> permissions{"permission.orders.active",
                                       "permission.restaurant.management"};
  const auto missing_permissions =
      GetMissingPermissions(permissions_config, roles, permissions);
  std::vector<std::string> expected = {"permission.restaurant.management"};
  ASSERT_EQ(missing_permissions, expected);
}

TEST(GetMissingPermissions, HasPermissionsTwoRoles) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  const auto& permissions_config =
      config.Get<::taxi_config::TaxiConfig>()
          .eats_restapp_authorizer_roles_permissions_settings;

  std::unordered_set<std::string> roles;
  roles.insert({"ROLE_OPERATOR", "ROLE_MANAGER"});

  std::vector<std::string> permissions{"permission.orders.active",
                                       "permission.restaurant.management"};
  const auto missing_permissions =
      GetMissingPermissions(permissions_config, roles, permissions);
  ASSERT_EQ(missing_permissions.size(), 0);
}

}  // namespace helpers::permissions
