#include "view.hpp"

#include <handlers/dependencies.hpp>

#include <models/errors.hpp>

namespace handlers::tests_v1_validate::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  try {
    dependencies.extra.processing_ng.ValidateResources(
        request.body.projects_root, request.body.path_offset,
        request.body.resources);
    return Response200();
  } catch (const processing::models::errors::ErrorWithLocation& err) {
    Response400 ret;
    ret.code = ::handlers::ConfigsInvalidCode::kBadConfig;
    ret.message = err.what();
    return ret;
  } catch (const std::exception& err) {
    Response400 ret;
    ret.code = ::handlers::ConfigsInvalidCode::kX400;
    ret.message = err.what();
    return ret;
  }
}

}  // namespace handlers::tests_v1_validate::post
