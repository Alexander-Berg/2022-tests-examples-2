#pragma once

#include <utils/translation/itranslator.hpp>

namespace eats_restapp_promo::utils {
class MockTranslator : public ITranslator {
 public:
  std::string GetTranslation(const std::string& locale,
                             const std::string& tanker_key) const override;

  std::string GetTranslation(const std::string& locale,
                             const std::string& tanker_key,
                             const ArgsList& args) const override;

  std::string GetTranslation(const std::string& locale,
                             const std::string& tanker_key,
                             const ArgsList& args, int count) const override;

  inline ~MockTranslator() = default;
};
}  // namespace eats_restapp_promo::utils
