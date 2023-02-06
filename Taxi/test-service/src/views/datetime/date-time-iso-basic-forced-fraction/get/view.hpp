#pragma once

#include <handlers/datetime/date-time-iso-basic-forced-fraction/get/request.hpp>
#include <handlers/datetime/date-time-iso-basic-forced-fraction/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::datetime_date_time_iso_basic_forced_fraction::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::datetime_date_time_iso_basic_forced_fraction::get
