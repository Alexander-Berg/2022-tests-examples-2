#pragma once

#include <gmock/gmock.h>
#include <models/partnerish_storage.hpp>
#include <userver/utest/utest.hpp>

namespace testing {

namespace partnerish = ::eats_partners::types::partrnerish;
using ::eats_partners::models::partrnerish::IStorage;

namespace search = ::eats_partners::types::search_request;

struct PartnerishStorageMock : public IStorage {
  MOCK_METHOD(partnerish::UuidToken, AddPartnerish,
              (partnerish::Partnerish partnerish), (override));
  MOCK_METHOD(std::optional<partnerish::Partnerish>, CheckPartnerishByEmail,
              (const partnerish::Email& email), (override));
  MOCK_METHOD(std::optional<partnerish::Partnerish>, GetPartnerishByUuid,
              (const partnerish::UuidToken& uuid), (override));
  MOCK_METHOD(void, AcceptPartnerishByUuid, (const partnerish::UuidToken& uuid),
              (override));
};

}  // namespace testing
