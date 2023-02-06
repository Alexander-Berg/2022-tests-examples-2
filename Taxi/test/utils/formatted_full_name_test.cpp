#include <userver/utest/utest.hpp>

#include <utils/formatted_full_name.hpp>

namespace {
struct NameParts {
  std::string first_name{};
  std::string last_name{};
  std::optional<std::string> middle_name{};
};
}  // namespace

UTEST(FormattedFullNameSuite, CheckShort) {
  const auto full_name =
      utils::FormattedFullName(NameParts{"Firstname", "Lastname"});
  ASSERT_EQ(full_name, "Lastname Firstname");
}
UTEST(FormattedFullNameSuite, CheckFull) {
  const auto full_name = utils::FormattedFullName(
      NameParts{"Firstname", "Lastname", "Middlename"});
  ASSERT_EQ(full_name, "Lastname Firstname Middlename");
}
