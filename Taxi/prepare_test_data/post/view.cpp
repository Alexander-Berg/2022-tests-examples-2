#include "view.hpp"

#include <handlers/dependencies.hpp>

namespace handlers::v1_internal_prepare_test_data::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  const auto& mmap_client = dependencies.extra.mmap_client;
  mmap_client.PrepareTestData(request.body.dir, request.body.abo_file,
                              request.body.mmap_file);
  return Response200{};
}

}  // namespace handlers::v1_internal_prepare_test_data::post
