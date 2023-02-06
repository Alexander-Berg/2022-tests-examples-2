#include "car_builder_test.hpp"

#include <mongo/names/db_cars/cars.hpp>

namespace names = utils::mongo::db::cars;

CarBuilder::CarBuilder(const std::string& park_id, const std::string& car_id) {
  builder.append(names::kParkId, park_id);
  builder.append(names::kCarId, car_id);
}

CarBuilder& CarBuilder::VIN(const std::string& vin) {
  builder.append(names::kVin, vin);
  return *this;
}

CarBuilder& CarBuilder::LicenseType(const std::string& license_type) {
  builder.append(names::kLicenseType, license_type);
  return *this;
}

CarBuilder& CarBuilder::Brand(const std::string& brand) {
  builder.append(names::kBrand, brand);
  return *this;
}

CarBuilder& CarBuilder::Model(const std::string& model) {
  builder.append(names::kModel, model);
  return *this;
}
CarBuilder& CarBuilder::NormalizedNumber(const std::string& number) {
  builder.append(names::kNumberNormalized, number);
  return *this;
}
CarBuilder& CarBuilder::CallSign(const std::string& call_sign) {
  builder.append(names::kCallSign, call_sign);
  return *this;
}
CarBuilder& CarBuilder::PermitDoc(const std::string& doc) {
  builder.append(names::kPermitDoc, doc);
  return *this;
}
CarBuilder& CarBuilder::PermitNum(const std::string& num) {
  builder.append(names::kPermitNum, num);
  return *this;
}
CarBuilder& CarBuilder::PermitSeries(const std::string& series) {
  builder.append(names::kPermitSeries, series);
  return *this;
}
CarBuilder& CarBuilder::RegistrationCertificate(const std::string& cert) {
  builder.append(names::kRegistrationCert, cert);
  return *this;
}

models::Car CarBuilder::Build() { return models::Car{builder.obj()}; }
