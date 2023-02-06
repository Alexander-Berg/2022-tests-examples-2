#include "mock_translator_test.hpp"

#include <algorithm>
#include <numeric>

#include <fmt/format.h>

namespace eats_restapp_promo::utils {
std::string MockTranslator::GetTranslation(
    const std::string& locale, const std::string& tanker_key) const {
  return fmt::format("{}_{}", locale, tanker_key);
}

std::string MockTranslator::GetTranslation(const std::string& locale,
                                           const std::string& tanker_key,
                                           const ArgsList& args) const {
  std::string args_as_string = std::accumulate(
      args.begin(), args.end(), std::string{}, [](std::string& acc, auto&& it) {
        return acc += fmt::format("{}-{}", it.first, it.second);
      });
  return fmt::format("{}_{}_{}", locale, tanker_key, args_as_string);
}

std::string MockTranslator::GetTranslation(const std::string& locale,
                                           const std::string& tanker_key,
                                           const ArgsList& args,
                                           int count) const {
  std::string args_as_string = std::accumulate(
      args.begin(), args.end(), std::string{}, [](std::string& acc, auto&& it) {
        return acc += fmt::format("{}-{}", it.first, it.second);
      });
  return fmt::format("{}_{}_{}_{}", locale, tanker_key, args_as_string, count);
}
}  // namespace eats_restapp_promo::utils
