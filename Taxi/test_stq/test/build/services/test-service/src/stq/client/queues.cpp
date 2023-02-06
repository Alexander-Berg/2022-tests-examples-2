#include "stq/client/queues.hpp"

#include <stq_clients/test.hpp>
#include <userver/formats/json/value_builder.hpp>

namespace stq {
template <>
TaskArguments<formats::json::Value> Serialize(
    stq_clients::test::Args&& args_struct) {
  auto args = formats::json::ValueBuilder{formats::json::Type::kArray};
  return {args.ExtractValue(),
          stq_clients::test::Serialize(
              std::move(args_struct),
              ::formats::serialize::To<::formats::json::Value>{})};
}
}
