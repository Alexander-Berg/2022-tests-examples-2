#include "mock_imager.hpp"

namespace zoneinfo {

ImageGetter MockImager(std::optional<ImageHandler> handler) {
  if (!handler) {
    handler = [](const ImageIntent& image, const std::string& application,
                 const std::optional<int>& size_hint) -> WebImage {
      WebImage result;
      result.url = image->GetTag().icon_tag + "_" +
                   image->GetTag().branding.value_or("no_branding") + "_" +
                   std::to_string(image->GetTag().skin_version.value_or(0)) +
                   "_for_" + application + "_" +
                   std::to_string(size_hint.value_or(0));
      return result;
    };
  }
  return std::make_shared<TestImager>(*handler);
}

}  // namespace zoneinfo
