#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/geobase/position/cityid/get/request.hpp>
#include <handlers/geobase/position/cityid/get/response.hpp>

namespace handlers::geobase_position_cityid::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::geobase_position_cityid::get
