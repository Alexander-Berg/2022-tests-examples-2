#pragma once

#include <helpers/impl/get_image_impl.hpp>

#include <functional>

#include <userver/utest/utest.hpp>

namespace zoneinfo {

using ImageHandler = std::function<std::optional<WebImage>(
    const ImageIntent&, const std::string&, const std::optional<int>&)>;

class TestImager : public WebImageGetter {
 public:
  TestImager(ImageHandler handler) : handler_(std::move(handler)) {}
  virtual ~TestImager() = default;

  virtual std::optional<WebImage> GetImage(
      const ImageIntent& image, const std::string& application,
      const std::optional<int>& size_hint) {
    return handler_(image, application, size_hint);
  }
  virtual WebImage GetImageThrows(const ImageIntent& image,
                                  const std::string& application,
                                  const std::optional<int>& size_hint) {
    auto result = GetImage(image, application, size_hint);
    if (result) return *result;
    throw ImageNotFound("test");
  }

 private:
  ImageHandler handler_;
};

ImageGetter MockImager(std::optional<ImageHandler> handler = std::nullopt);

}  // namespace zoneinfo
