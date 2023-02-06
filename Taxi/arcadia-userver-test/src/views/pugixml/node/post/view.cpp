#include "view.hpp"

#include <pugixml.hpp>

namespace handlers::pugixml_node::post {
namespace {

class StringWriter : public pugi::xml_writer {
 public:
  explicit StringWriter(std::string& out) : out_(out) {}

  void write(const void* data, size_t size) override {
    out_.append(static_cast<const char*>(data), size);
  }

 private:
  std::string& out_;
};

}  // namespace

Response View::Handle(Request&& request, Dependencies&& /*dependencies*/
) {
  Response200 response;

  pugi::xml_document doc;
  auto node = doc.append_child(request.body.name.c_str());
  node.append_child(pugi::node_pcdata).set_value(request.body.value.c_str());
  if (request.body.attributes) {
    for (const auto& [attr_name, attr_value] : request.body.attributes->extra) {
      node.append_attribute(attr_name.c_str()).set_value(attr_value.c_str());
    }
  }
  StringWriter writer{response.body};
  doc.save(writer, "", pugi::format_raw);

  return response;
}

}  // namespace handlers::pugixml_node::post
