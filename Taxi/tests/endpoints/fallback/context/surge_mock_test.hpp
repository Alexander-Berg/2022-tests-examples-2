#pragma once

#include <endpoints/fallback/core/context/surge.hpp>

namespace routestats::test {

class SurgeMock : public fallback::SurgeStorage {
 public:
  SurgeMock(fallback::SurgeInfo surge_info) : surge_info_(surge_info){};

  void StartLoadSurge() override{};
  void LoadSurge() override{};

  std::optional<fallback::SurgeInfo> GetSurgeInfo() const override {
    return surge_info_;
  };
  std::optional<fallback::Surge> GetSurgeByCategory(
      const std::string& cat) const override {
    if (surge_info_.surge_map.count(cat)) return surge_info_.surge_map.at(cat);
    return std::nullopt;
  };

 private:
  fallback::SurgeInfo surge_info_;
};
}  // namespace routestats::test
