#include "set_integer_value_mapper.hpp"

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

TEST(Mappers, SetIntegerValueMapperTest) {
  auto json_mapper =
      eventus::mappers::SetIntegerValueMapper(std::vector<OperationArgument>{
          {"dst_key", kDstKey}, {"value", static_cast<double>(42)}});

  eventus::mappers::Event event({});
  json_mapper.Map(event);

  ASSERT_TRUE(event.HasKey(kDstKey));
  ASSERT_EQ(event.Get<int>(kDstKey), 42);
}
