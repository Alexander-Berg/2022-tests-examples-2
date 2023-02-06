#include <gtest/gtest.h>

#include <helpers/agglomerations.hpp>

namespace tests {

class AgglomerationsLogicTest final : public helpers::IAgglomerationsLogic {
 public:
  std::string GetAgglomeration(
      const std::string& /*tariff_zone_path*/) const final {
    return "br_moscow";
  }
};

class AgglomerationsLogicWrong final : public helpers::IAgglomerationsLogic {
 public:
  std::string GetAgglomeration(
      const std::string& /*tariff_zone_path*/) const final {
    return "not_existed";
  }
};

helpers::AgglomerationLogicPtr CreateAgglomerationsLogic() {
  return std::make_unique<AgglomerationsLogicTest>();
}

TEST(Agglomerations, Get) {
  const std::string zone_path =
      "/br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/"
      "br_moscow_adm";
  const std::vector<std::string> expected = {
      "/br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/"
      "br_moscow_adm",
      "/br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow"};
  EXPECT_EQ(
      helpers::GetPathsToAgglomeration(zone_path, CreateAgglomerationsLogic()),
      expected);

  const std::string zone_path2 =
      "br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/"
      "br_moscow_adm/br_msk_center";
  const std::vector<std::string> expected2 = {
      "br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/"
      "br_moscow_adm/br_msk_center",
      "br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/"
      "br_moscow_adm",
      "br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow"};
  EXPECT_EQ(
      helpers::GetPathsToAgglomeration(zone_path2, CreateAgglomerationsLogic()),
      expected2);

  EXPECT_THROW(helpers::GetPathsToAgglomeration(
                   zone_path, std::make_unique<AgglomerationsLogicWrong>()),
               std::runtime_error);
}

}  // namespace tests
