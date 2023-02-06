#include <userver/utest/utest.hpp>

#include <models/roles.hpp>
#include "roles_storage_mock.hpp"

namespace testing {

using ::eats_partners::models::roles::Storage;

struct RolesStorageTest : public Test {
  std::shared_ptr<RolesStoragePgMock> storage_mock;
  Storage storage;

  RolesStorageTest()
      : storage_mock(std::make_shared<RolesStoragePgMock>()),
        storage(storage_mock) {}
};

TEST_F(RolesStorageTest, should_call_GetRoles) {
  EXPECT_CALL(*storage_mock, GetRoles()).Times(1);
  storage.GetRoles();
}

}  // namespace testing
