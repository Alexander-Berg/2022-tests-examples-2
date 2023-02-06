#include "view.hpp"

#include <fmt/format.h>

#include <lz4/lz4.hpp>

namespace handlers::lz4_decompress::post {

Response View::Handle(Request&& request, Dependencies&&) {
  return {lz4::Decompress(request.body)};
}

std::string View::GetRequestBodyForLogging(const Request*,
                                           const std::string& request_body) {
  return fmt::format("<binary buffer, total {} bytes>", request_body.size());
}

}  // namespace handlers::lz4_decompress::post
