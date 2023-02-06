#include "view.hpp"

#include <fmt/format.h>

#include <lz4/lz4.hpp>

namespace handlers::lz4_compress::post {

Response View::Handle(Request&& request, Dependencies&&) {
  return {lz4::Compress(request.body)};
}

std::string View::GetResponseForLogging(
    const Response&, const std::string& serialized_response,
    ::server::request::RequestContext& context) {
  return GetNonSchemaResponseForLogging(serialized_response, context);
}

std::string View::GetNonSchemaResponseForLogging(
    const std::string& response, ::server::request::RequestContext&) {
  return fmt::format("<binary buffer, total {} bytes>", response.size());
}

}  // namespace handlers::lz4_compress::post
