#pragma once

#include <fstream>

#include <models/cached/cities.hpp>
#include <models/countries.hpp>
#include <utils/helpers/json.hpp>
#include <utils/translation_mock.hpp>

struct JSONFixtures {
  static std::string Load(const std::string& filename) {
    const std::string full_name =
        std::string(SOURCE_DIR) + "/tests/static/" + filename;
    std::ifstream stream(full_name);
    assert(stream);
    std::string str((std::istreambuf_iterator<char>(stream)),
                    std::istreambuf_iterator<char>());
    return str;
  }

  static mongo::BSONObj GetFixtureBSON(const std::string& name) {
    return mongo::fromjson(Load(name));
  }

  static Json::Value GetFixtureJSON(const std::string& name) {
    return utils::helpers::ParseJson(Load(name));
  }

  static l10n::TranslationsPtr GetMockTranslations() {
    static const std::shared_ptr<MockTranslations> translations{
        new MockTranslations};
    return translations;
  };

  static std::shared_ptr<models::CitiesModel> GetMockCities() {
    std::string str = Load("db_cities.json");
    auto cities = std::make_shared<models::CitiesModel>();
    Json::Value root = utils::helpers::ParseJson(str);
    for (const auto& json : root) {
      models::City city;
      city.country = json["country"].asString();
      if (json.isMember("eng")) city.english_name = json["eng"].asString();
      cities->cities[json["_id"].asString()] = city;
    }
    return cities;
  }
};
