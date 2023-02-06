#pragma once

#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>
#include "helpers/restric_send_helper.hpp"

namespace testing {

class RestrictSendHelperMock
    : public eats_restapp_communications::helpers::IConfigHelper {
 public:
  MOCK_METHOD(bool, Disabled,
              (const eats_restapp_communications::types::Recipient& recipient,
               const std::string& event),
              (const, override));
};

}  // namespace testing
