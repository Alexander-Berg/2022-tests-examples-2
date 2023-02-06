#pragma once

#include "internal/plaque.hpp"

#include <functional>

namespace sweet_home::mocks {

using HandlerGetPlaques =
    std::function<std::vector<plaque::Plaque>(const std::string&)>;

class PlaqueRepositoryMock : public plaque::PlaqueRepository {
 private:
  HandlerGetPlaques handler_;

 public:
  PlaqueRepositoryMock(){};

  void SetupGetPlaques(const HandlerGetPlaques& handle) { handler_ = handle; }

  std::vector<plaque::Plaque> GetPlaques(
      const std::string& service_id) const override {
    return handler_(service_id);
  }
};

}  // namespace sweet_home::mocks
