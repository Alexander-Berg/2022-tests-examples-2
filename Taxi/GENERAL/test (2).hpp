#pragma once

#include <fastcgi2/component.h>
#include <fastcgi2/handler.h>

#include <config/config_component.hpp>

#include <handler_util/base.hpp>
#include <handlers/base.hpp>
#include <models/experiments3_cache_manager.hpp>
#include <utils/data_provider.hpp>

namespace handlers {

class TestHandler : public handlers::BaseExp3Handler {
 public:
  using handlers::BaseExp3Handler::BaseExp3Handler;

  virtual void onLoad() final;
  virtual void onUnload() final;

 protected:
  virtual void Handle(fastcgi::Request& request,
                      ::handlers::BaseContext& context) final;

 private:
  const utils::DataProvider<experiments3::models::CacheManager>*
      experiments3_cache_ = nullptr;
};

}  // namespace handlers
