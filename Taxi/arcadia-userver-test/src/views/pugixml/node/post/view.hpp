#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/pugixml/node/post/request.hpp>
#include <handlers/pugixml/node/post/response.hpp>

namespace handlers::pugixml_node::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::pugixml_node::post
