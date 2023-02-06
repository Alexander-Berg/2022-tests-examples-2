#include <userver/utest/utest.hpp>

#include <models/partner_activity_storage.hpp>
#include "partner_activity_storage_mock.hpp"

namespace testing {

using ::eats_partners::models::partner_activity::Storage;

struct PartnerActivityStorageTest : public Test {
  std::shared_ptr<PartnerActivityStorageMock> storage_mock;
  Storage storage;

  const std::vector<PartnerId> partner_ids{PartnerId{42}};

  PartnerActivityStorageTest()
      : storage_mock(std::make_shared<PartnerActivityStorageMock>()),
        storage(storage_mock) {}
};

TEST_F(PartnerActivityStorageTest, should_call_GetActivity_if_later_not_set) {
  EXPECT_CALL(*storage_mock, GetActivity(partner_ids)).Times(1);
  storage.GetActivity(partner_ids, std::nullopt);
}

TEST_F(PartnerActivityStorageTest,
       should_call_GetActivityLimited_if_later_set) {
  EXPECT_CALL(*storage_mock, GetActivityLimited(partner_ids, _)).Times(1);
  storage.GetActivity(partner_ids, std::chrono::system_clock::time_point());
}

}  // namespace testing
