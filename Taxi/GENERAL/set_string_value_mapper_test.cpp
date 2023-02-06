#include "set_string_value_mapper.hpp"

#include <string>
#include <vector>

#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/value.hpp>
#include <userver/formats/json/value_builder.hpp>
#include <userver/utest/utest.hpp>

using eventus::common::OperationArgs;
using eventus::common::OperationArgument;
using OperationArgsV = std::vector<eventus::common::OperationArgumentType>;

namespace {

const auto kDstKey = "destination";

}

TEST(Mappers, SetStringValueMapperTest) {
  auto json_mapper = eventus::mappers::SetStringValueMapper(
      std::vector<OperationArgument>{{"dst_key", kDstKey}, {"value", "BMO"}});

  eventus::mappers::Event event({});
  json_mapper.Map(event);

  ASSERT_TRUE(event.HasKey(kDstKey));
  ASSERT_EQ(event.Get<std::string>(kDstKey), std::string("BMO"));
}
