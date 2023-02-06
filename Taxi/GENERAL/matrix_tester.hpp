#pragma once

#include <utility>
#include "vendors/yamaps/yamaps_router.hpp"
namespace clients::routing {

class Tester {
 public:
  template <class... T>
  std::string MakeMatrixUrl(T... args) const {
    return target->MakeMatrixUrl(std::forward<T>(args)...);
  }

  template <class... T>
  auto ParseMatrixInfo(T... args) const {
    return target->ParseMatrixInfo(std::forward<T>(args)...);
  }

  template <class... T>
  auto FetchMatrixInfo(T... args) const {
    return target->FetchMatrixInfo(std::forward<T>(args)...);
  }

  std::shared_ptr<YaMapsRouter> target;
};

}  // namespace clients::routing
