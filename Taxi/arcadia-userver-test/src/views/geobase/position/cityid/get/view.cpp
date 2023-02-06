#include "view.hpp"

#include <geobase/utils/city.hpp>

namespace handlers::geobase_position_cityid::get {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  response.city_id = geobase::GetCityIdByPosition(request.lon, request.lat,
                                                  *dependencies.lookup);

  return response;
}

}  // namespace handlers::geobase_position_cityid::get
