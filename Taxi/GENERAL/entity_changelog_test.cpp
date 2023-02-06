#include "entity_changelog.hpp"

#include <gtest/gtest.h>

#include <utils/helpers/bson.hpp>

using helpers::change_history::MakeDefaultProvider;
using helpers::change_history::Value;
using helpers::change_history::internal::CalculateDiff;

using ValueMap = std::unordered_map<std::string, Value>;

const helpers::change_history::MongoCSharpFieldMap kFields{
    {"bool", MakeDefaultProvider("SomeBool")},  //
};

namespace helpers::change_history {

bool operator==(const Value& l, const Value& r) {
  return l.current == r.current && l.old == r.old;
}

inline void PrintTo(const Value& v, ::std::ostream* os) {
  *os << "(" << v.old << ", " << v.current << ")";
}

}  // namespace helpers::change_history

TEST(ChangeLog, Diff) {
  const auto& diff1 = CalculateDiff(BSON("bool" << true), BSON("bool" << true),
                                    {}, kFields, {});
  ASSERT_EQ(ValueMap{}, diff1);

  const auto& diff2 = CalculateDiff(BSON("bool" << true), {},
                                    BSON("bool" << true), kFields, {});
  ASSERT_EQ((ValueMap{{"SomeBool", {"true", ""}}}), diff2);

  const auto& diff3 = CalculateDiff({}, BSON("bool" << true), {}, kFields, {});
  ASSERT_EQ((ValueMap{{"SomeBool", {"", "true"}}}), diff3);

  const auto& diff4 = CalculateDiff(BSON("bool" << true), BSON("bool" << false),
                                    {}, kFields, {});
  ASSERT_EQ((ValueMap{{"SomeBool", {"true", "false"}}}), diff4);
}
