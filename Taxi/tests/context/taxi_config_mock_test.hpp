#pragma once

#include <core/context/taxi_configs.hpp>
#include <taxi_config/taxi_config.hpp>

#include <functional>

#include <testing/taxi_config.hpp>

namespace routestats::test {

class TaxiConfigsMock : public core::TaxiConfigs {
 public:
  TaxiConfigsMock()
      : storage_(dynamic_config::MakeDefaultStorage({})),
        snapshot_(storage_.GetSnapshot()) {}

  TaxiConfigsMock(dynamic_config::StorageMock storage)
      : storage_(std::move(storage)), snapshot_(storage_.GetSnapshot()) {}

  const dynamic_config::Snapshot& GetSnapshot() const override {
    return snapshot_;
  }

 private:
  dynamic_config::StorageMock storage_;
  dynamic_config::Snapshot snapshot_;
};

}  // namespace routestats::test
