#pragma once

#include <clients/graphite.hpp>
#include <common/test_config.hpp>
#include <components/graphite.hpp>
#include <config/config.hpp>
#include <handlers/context.hpp>
#include <utils/prof.hpp>

class MockHeadersContext {
 public:
  MockHeadersContext()
      : config_(config::DocsMapForTest()), time_storage_("test") {}

  handlers::Context GetContext() { return {config_, graphite_, log_extra_}; }
  TimeStorage& GetTimeStorage() { return time_storage_; }
  config::Config& GetConfigRef() { return config_; }

 private:
  config::Config config_;
  clients::Graphite graphite_;
  TimeStorage time_storage_;
  LogExtra log_extra_;
};
