#pragma once

#include <string>

#include <models/personalization.hpp>

namespace eats_products::tests {

class PersonalizationDelegateForTesting
    : public models::Personalization::Delegate {
 public:
  void SetPersonalizationTypes(const models::PersonalizationTypes& types) {
    personalization_types_ = types;
  }

  void SetUserIncomeLevel(const std::string& income_level) {
    income_level_ = income_level;
  }

  void SetIncomeByBrand(const std::string& income_by_brand) {
    income_by_brand_ = income_by_brand;
  }

  void SetDefaultTableName(const std::string& default_table_name) {
    default_table_name_ = default_table_name;
  }

  void SetTableNameTemplate(const std::string& table_name_template) {
    table_name_template_ = table_name_template;
  }

  void SetCategoriesInfo(const CategoriesInfo& info) { info_ = info; }

  // models::Personalization::Delegate overrides:
  const models::PersonalizationTypes& GetPersonalizationTypes() const override {
    return personalization_types_;
  }

  const std::string& GetUserIncomelevel() override { return income_level_; }

  std::string GetIncomeLevelByBrand(models::BrandId) const override {
    return income_by_brand_;
  }

  const std::string& GetProductsTableName() const override {
    return default_table_name_;
  }

  const std::string& GetCategoriesTableName() const override {
    return default_table_name_;
  }

  const std::string& GetProductsTableTemplate() const override {
    return table_name_template_;
  }

  const std::string& GetCategoriesTableTemplate() const override {
    return table_name_template_;
  }

  const CategoriesInfo& GetCategoriesInfo() override { return info_; }

 private:
  models::PersonalizationTypes personalization_types_;
  std::string income_level_;
  std::string income_by_brand_;
  std::string default_table_name_;
  std::string table_name_template_;
  CategoriesInfo info_;
};

}  // namespace eats_products::tests
