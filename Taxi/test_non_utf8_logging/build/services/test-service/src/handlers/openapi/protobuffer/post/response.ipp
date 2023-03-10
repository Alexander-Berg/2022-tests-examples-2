#ifndef USERVER_CODEGEN_IPP_INSTANTIATION_GUARD
#error DO NOT INCLUDE THIS FILE! INCLUDE THE FILE WITH *.hpp EXTENSION!
#endif

/* THIS FILE IS AUTOGENERATED, DON'T EDIT! */

// This file was generated from file(s):
// taxi/uservices/services/test-service/docs/yaml/api/api.yaml,
// taxi/uservices/services/test-service/docs/yaml/api/openapi.yaml

#include <handlers/openapi/protobuffer/post/response.hpp>

#include <boost/algorithm/string/join.hpp>

#include <codegen/impl/response_visitors.hpp>
#include <userver/formats/json/serialize.hpp>
#include <userver/formats/json/serialize_container.hpp>  // for std::optional
#include <userver/formats/json/value_builder.hpp>
#include <userver/utils/assert.hpp>

#include <codegen/impl/convert.hpp>
#include <codegen/impl/get_validation_length.hpp>
#include <codegen/impl/optional_convert.hpp>
#include <codegen/impl/parsers.hpp>
#include <cstring>
#include <unordered_set>
#include <userver/formats/common/meta.hpp>
#include <userver/formats/json/string_builder.hpp>
#include <userver/logging/log.hpp>
#include <userver/utils/assert.hpp>
#include <userver/utils/datetime/from_string_saturating.hpp>
#include <userver/utils/underlying_value.hpp>

#include <codegen/impl/convert.hpp>

namespace handlers::openapi_protobuffer::post {

std::string Response200::ToString() const { return body; }

void FillHttpResponse(
    [[maybe_unused]] ::server::http::HttpResponse& http_response,
    [[maybe_unused]] const Response200& response)
{
  http_response.SetContentType("application/protobuf");
}

std::string ToString(const Response& response)
{
  return ::codegen::impl::ResponseVisitorToString()(response);
}

}
