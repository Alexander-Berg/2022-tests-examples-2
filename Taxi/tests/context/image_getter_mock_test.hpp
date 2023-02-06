#pragma once

#include <functional>

#include <core/context/images.hpp>

namespace routestats::test {

class ImageGetterMock : public core::ImageGetter {
 public:
  template <class F>
  ImageGetterMock(F&& handler) : handler_(std::move(handler)) {}

  std::optional<core::Image> GetImage(
      const std::string& tag, const std::optional<int> size_hint,
      const std::optional<std::string>& theme) override {
    return handler_(tag, size_hint, theme);
  }

 private:
  using ImageGetterHandler = std::function<std::optional<core::Image>(
      const std::string&, const std::optional<int>,
      const std::optional<std::string>&)>;

  ImageGetterHandler handler_;
};

}  // namespace routestats::test
