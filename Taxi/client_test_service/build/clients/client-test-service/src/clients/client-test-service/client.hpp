/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

#pragma once

#include <clients/codegen/command_control.hpp>
#include <clients/codegen/response_future_fwd.hpp>

#include <clients/client-test-service/definitions.hpp>
#include <clients/client-test-service/exception.hpp>
#include <clients/client-test-service/requests.hpp>
#include <clients/client-test-service/responses.hpp>

namespace clients::http {
class ResponseFuture;
}

namespace clients::client_test_service {

using CommandControl = ::clients::codegen::CommandControl;

/// @brief Client for 'Service for clients codegen testing'
///
/// Version: 0.1
class Client {
 public:
  Client() = default;
  Client(const Client&) = delete;
  Client(Client&&) = delete;
  virtual ~Client();

  Client& operator=(const Client&) = delete;
  Client& operator=(Client&&) = delete;

  /// URL: /v1/my-arg/smth
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v1_my_arg_smth::get::Exception
  virtual v1_my_arg_smth::get::Response V1MyArgSmthGet(
      const v1_my_arg_smth::get::Request& request,
      const CommandControl& command_control = {}) const = 0;

  virtual ::clients::codegen::ResponseFuture<v1_my_arg_smth::get::Response>
  AsyncV1MyArgSmthGet(const v1_my_arg_smth::get::Request& request,
                      const CommandControl& command_control = {}) const = 0;

  /// URL: /v1/my-arg/smth
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v1_my_arg_smth::post::Exception
  /// @throw v1_my_arg_smth::post::Response404
  virtual v1_my_arg_smth::post::Response V1MyArgSmthPost(
      const v1_my_arg_smth::post::Request& request,
      const CommandControl& command_control = {}) const = 0;

  virtual ::clients::codegen::ResponseFuture<v1_my_arg_smth::post::Response>
  AsyncV1MyArgSmthPost(const v1_my_arg_smth::post::Request& request,
                       const CommandControl& command_control = {}) const = 0;

  /// URL: /v2/smth
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v2_smth::get::Exception
  template <class... Args>
  void V2SmthGet(const v2_smth::get::Request& /*request*/,
                 const Args&...) const {
    static_assert(false && sizeof...(Args),
                  "Operation is not supported in clients");
  }

  /// URL: /v2/smth
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v2_smth::post::Exception
  template <class... Args>
  void V2SmthPost(const v2_smth::post::Request& /*request*/,
                  const Args&...) const {
    static_assert(false && sizeof...(Args),
                  "Operation is not supported in clients");
  }

  /// URL: /v3/smth
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v3_smth::get::Exception
  virtual v3_smth::get::Response V3SmthGet(
      const CommandControl& command_control = {}) const = 0;

  virtual ::clients::codegen::ResponseFuture<v3_smth::get::Response>
  AsyncV3SmthGet(const CommandControl& command_control = {}) const = 0;

  /// URL: /v3/smth
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw v3_smth::post::Exception
  template <class... Args>
  void V3SmthPost(const v3_smth::post::Request& /*request*/,
                  const Args&...) const {
    static_assert(false && sizeof...(Args),
                  "Operation is not supported in clients");
  }

  /// URL: /
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw root_::get::Exception
  virtual root_::get::Response NsGet(
      const root_::get::Request& request,
      const CommandControl& command_control = {}) const = 0;

  virtual ::clients::codegen::ResponseFuture<root_::get::Response> AsyncNsGet(
      const root_::get::Request& request,
      const CommandControl& command_control = {}) const = 0;

  /// URL: /
  /// @param request запрос
  /// @param command_control специфичные настройки timeout/retries. Если
  /// std::nullopt, то используется значение из TaxiConfig.
  ///
  /// @throw root_::post::Exception
  /// @throw root_::post::Response404
  virtual root_::post::Response NsPost(
      const root_::post::Request& request,
      const CommandControl& command_control = {}) const = 0;

  virtual ::clients::codegen::ResponseFuture<root_::post::Response> AsyncNsPost(
      const root_::post::Request& request,
      const CommandControl& command_control = {}) const = 0;
};

}
