/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/schemas/schemas/services/client-test-service/api/api-3.0.yaml,
// taxi/schemas/schemas/services/client-test-service/api/api.yaml

#pragma once

#include <gmock/gmock.h>
#include <userver/utest/utest.hpp>

#include <clients/client-test-service/client.hpp>
#include "client_mock_base.hpp"

namespace clients::client_test_service {

/// @brief Mock for Service for clients codegen testing client
///
/// Derive from this class and override functions you're interested in.
///
/// Version: 0.1
class ClientGMock: public ClientMockBase {
 public:
  /// URL: /v1/my-arg/smth
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v1_my_arg_smth::get::Exception
  MOCK_METHOD(v1_my_arg_smth::get::Response, V1MyArgSmthGet,
              (const v1_my_arg_smth::get::Request& /*request*/,
               const CommandControl& /*command_control*/
               ), (const, override));

  /// URL: /v1/my-arg/smth
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v1_my_arg_smth::post::Exception
  /// @throw v1_my_arg_smth::post::Response404
  MOCK_METHOD(v1_my_arg_smth::post::Response, V1MyArgSmthPost,
              (const v1_my_arg_smth::post::Request& /*request*/,
               const CommandControl& /*command_control*/
               ), (const, override));

  /// URL: /v2/smth
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v2_smth::get::Exception

  /// URL: /v2/smth
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v2_smth::post::Exception

  /// URL: /v3/smth
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v3_smth::get::Exception
  MOCK_METHOD(v3_smth::get::Response, V3SmthGet,
              (const CommandControl& /*command_control*/
               ), (const, override));

  /// URL: /v3/smth
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v3_smth::post::Exception

  /// URL: /
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw root_::get::Exception
  MOCK_METHOD(root_::get::Response, NsGet,
              (const root_::get::Request& /*request*/,
               const CommandControl& /*command_control*/
               ), (const, override));

  /// URL: /
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw root_::post::Exception
  /// @throw root_::post::Response404
  MOCK_METHOD(root_::post::Response, NsPost,
              (const root_::post::Request& /*request*/,
               const CommandControl& /*command_control*/
               ), (const, override));
};

}