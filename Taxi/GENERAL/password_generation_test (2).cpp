#include <gtest/gtest.h>

#include <boost/algorithm/string.hpp>
#include <unordered_set>

#include <handlers/password_generation.hpp>

namespace signal_device_registration_api::handlers {

TEST(PasswordGeneration, GeneratePassword) {
  constexpr std::size_t kAttempts = 10;

  std::unordered_set<std::string> passwords;
  for (std::size_t i = 0; i < kAttempts; i++) {
    auto password = GeneratePassword();

    std::vector<std::string> words;
    boost::split(words, password, boost::is_any_of(kWordsSeparator),
                 boost::token_compress_on);
    EXPECT_EQ(kWordsInPassword, words.size());

    passwords.insert(std::move(password));
  }

  EXPECT_EQ(kAttempts, passwords.size());
}

}  // namespace signal_device_registration_api::handlers
