#include <resources/test/resource.hpp>

#include <userver/testsuite/testpoint.hpp>

namespace resources::test {

Processor::Out Processor::operator()(Processor::In&& input) const {
  Out output;
  output.depot_id = input.depot_id;
  output.timestamp = ::utils::datetime::Now();
  // output.data is Null

  TESTPOINT_CALLBACK("parsed_data_processing",
                     ::formats::json::ValueBuilder{input}.ExtractValue(),
                     [&output](const ::formats::json::Value& val) {
                       output.data.extra = val;
                     });

  return output;
}

js_pipeline::resource_management::InstancePtr Resource::WrapResult(
    formats::json::Value&& val) const {
  TESTPOINT("wrap_serialized_result", val);
  return Base::WrapResult(std::move(val));
}

}  // namespace resources::test
