#include "view.hpp"

namespace handlers::ytlib_smoke_test::post {

Response View::Handle(Request&& request, Dependencies&& dependencies) {
  Response200 response;

  auto& client = dependencies.extra.ytlib.GetYtClient(request.body.yt_cluster);
  auto cursor =
      client.SelectRows(fmt::format("id, value FROM [{}]", request.body.table));
  for (auto& row : cursor) {
    response.items.push_back(
        {row.Get<std::string>(0), row.Get<std::string>(1)});
  }

  return response;
}

}  // namespace handlers::ytlib_smoke_test::post
