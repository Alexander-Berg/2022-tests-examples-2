#include <gtest/gtest.h>

#include <json/json.h>
#include <boost/algorithm/string.hpp>
#include <mongo/mongo.hpp>

#include "adaptors/geoareas.hpp"
#include "utils/geoareas_fixture.hpp"
#include "utils/jsonfixtures.hpp"

#include <vector>

namespace geoarea {

TEST(GeohashIndex, test_geohash_index) {
  // load geoareas list and its index
  const auto& geoareas_bson =
      JSONFixtures::GetFixtureBSON("geoareas_for_hash.json");
  Geoarea::geoarea_dict_t geoareas =
      GeoareasFixture::LoadFromBSONArray(geoareas_bson);
  const Geoarea::geoarea_hash_t& hash = BuildGeohashIndex(geoareas);

  // test cases and its expectations
  std::vector<std::pair<Geoarea::point_t, std::set<std::string>>> expectations{
      {{37.587581, 55.734584},
       {"Yandex", "russia", "mkad", "hamovniki", "msk_obl"}},
      {{37.566510, 55.743185}, {"kiyevsky", "russia", "mkad", "msk_obl"}},
      {{37.606020, 55.633814}, {"russia", "mkad", "msk_obl"}},
      {{37.855141, 55.760515}, {"russia", "msk_obl"}},
      {{112.759106, 63.510185}, {"russia"}},
      {{-81.529643, 40.491458}, {}},
  };

  // perform test cases checking
  for (const auto& i : expectations) {
    const Geoarea::geoarea_list_t& geoareas = QueryGeohashIndex(hash, i.first);
    std::set<std::string> names;
    std::transform(geoareas.cbegin(), geoareas.cend(),
                   std::inserter(names, names.begin()),
                   [](const Geoarea::Sptr& geoarea) { return geoarea->id(); });
    EXPECT_EQ(names, i.second);
  }
}

}  // namespace geoarea
