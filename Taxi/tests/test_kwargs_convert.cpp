#include <gtest/gtest.h>

#include <common/types/converters.hpp>
#include <stq/stq.hpp>

namespace tests {

namespace {
template <class T, class Data>
T FromToStq(const Data& data) {
  return std::get<T>(
      stq::FromStqKwargs(stq::ToStqKwargs(types::RuleVariantData(data)))
          .AsVariant());
}
}  // namespace

TEST(StqConversions, FraudData) {
  types::RuleFraudData data;
  data.drivers = {{"dbid", "uuid"}};
  data.rule_type = types::RuleType::kDriverFix;
  data.idempotency_key = "key";
  ASSERT_EQ(data, FromToStq<types::RuleFraudData>(data));
}

TEST(StqConversions, PayData) {
  types::RulePayData data;
  data.drivers = {{"dbid", "uuid"}};
  data.rule_type = types::RuleType::kDriverFix;
  data.idempotency_key = "key";
  data.doc_id = 100;
  ASSERT_EQ(data, FromToStq<types::RulePayData>(data));
}
}  // namespace tests
