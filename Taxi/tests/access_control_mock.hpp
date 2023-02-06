#pragma once

#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>
#include "models/access_control.hpp"

namespace testing {

using PartnerId = ::eats_partners::types::partner::Id;
using RoleTemplate = ::eats_partners::types::role_template::RoleTemplate;
using ::eats_partners::models::access_control::IAccessControl;

class AccessControlMock : public IAccessControl {
 public:
  MOCK_METHOD(void, CreateUser,
              (const PartnerId& partner_id,
               const std::vector<RoleTemplate>& roles_templates),
              (const, override));
  MOCK_METHOD(void, UpdateUser,
              (const PartnerId& partner_id,
               const std::vector<RoleTemplate>& roles_templates),
              (const, override));
};

}  // namespace testing

namespace eats_partners::types::role_template {
inline bool operator==(const RoleTemplate& lhs, const RoleTemplate& rhs) {
  return std::tie(lhs.role_slug, lhs.ac_group_slug) ==
         std::tie(rhs.role_slug, rhs.ac_group_slug);
}
}  // namespace eats_partners::types::role_template
