#pragma once

struct GeoareasFixture {
  static Geoarea::geoarea_dict_t LoadFromBSONArray(
      const mongo::BSONObj& geoareas_bson) {
    Geoarea::geoarea_dict_t geoareas;
    const int xz = geoareas_bson.nFields();
    const char* kType = "t";
    const char* kGeometry = "geometry";
    const char* kCoordinates = "coordinates";
    const char* kArea = "area";

    for (int i = 0; i < xz; ++i) {
      const auto& bs = geoareas_bson[i];
      const auto name = bs["name"].String();
      const auto& doc = bs;

      Geoarea::polygon_t polygon;
      if (doc[kGeometry].ok()) {
        const auto geo_coords = doc[kGeometry][kCoordinates];
        const auto shell = utils::mongo::ToArray(geo_coords)[0];
        for (const auto& coordinate : utils::mongo::ToArray(shell)) {
          auto dimensions = utils::mongo::ToArray(coordinate);
          auto lon = utils::mongo::ToDouble(dimensions[0]);
          auto lat = utils::mongo::ToDouble(dimensions[1]);
          boost::geometry::append(polygon, Geoarea::point_t(lon, lat));
        }
      }

      double area = doc[kArea].ok() ? utils::mongo::ToDouble(doc[kArea]) : 0.0;

      Geoarea::type_t geoarea_type;
      if (doc[kType].ok() && doc[kType].type() == mongo::BSONType::Array) {
        const auto& types = utils::mongo::ToArray(doc[kType]);
        for (const auto& maybe_type_str : types) {
          if (maybe_type_str.type() == mongo::BSONType::String) {
            std::string type_str = boost::algorithm::to_lower_copy(
                utils::mongo::ToString(maybe_type_str));
            if (type_str == "airport") {
              geoarea_type |= Geoarea::Type::Airport;
            }
            if (type_str == "st") {
              geoarea_type |= Geoarea::Type::SignificantTransfer;
            }
          }
        }
      }

      geoareas.emplace(name, std::make_shared<Geoarea>(
                                 name, name, 0, polygon, area, geoarea_type,
                                 boost::none, Geoarea::date_t()));
    }
    return geoareas;
  }
};
