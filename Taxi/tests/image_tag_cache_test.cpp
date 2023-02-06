#include <fmt/format.h>

#include <testing/taxi_config.hpp>
#include <userver/utest/utest.hpp>

#include <image_tag_cache/models/image_tag_cache.hpp>

namespace {

using ImageTagCache = image_tag_cache::models::ImageTagCache;
const std::string kBaseUrl = "https://tc.mobile.yandex.net/static/images/{}";

}  // namespace

UTEST(ImageTagCacheTest, ItemWithoutRevision) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"}, {{"app1", 100}}, std::nullopt, "id1", {}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_EQ(fmt::format(kBaseUrl, "id1"),
            cache.GetImageUrl("tag1", 100, "app1", config).value());

  ASSERT_EQ(fmt::format(kBaseUrl, "id1"),
            cache.GetImageUrl("tag1:rev1", 100, "app1", config).value());
}

UTEST(ImageTagCacheTest, UnknownRevision) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"}, {{"app1", 100}}, std::nullopt, "id1", {{"rev1", "id_rev1"}}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_EQ(fmt::format(kBaseUrl, "id_rev1"),
            cache.GetImageUrl("tag1:rev1", 100, "app1", config).value_or(""));

  ASSERT_EQ(
      fmt::format(kBaseUrl, "id_rev1"),
      cache.GetImageUrl("tag1:<unknown>", 100, "app1", config).value_or(""));
}

UTEST(ImageTagCacheTest, MultipleSizeTags) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  image_tag_cache::models::ImageTagItems items{{{"tag1"},
                                                {{"app1", 100}, {"app1", 200}},
                                                std::nullopt,
                                                "id1",
                                                {{"rev1", "id_rev1"}}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_EQ(fmt::format(kBaseUrl, "id_rev1"),
            cache.GetImageUrl("tag1", 100, "app1", config).value_or(""));

  ASSERT_EQ(fmt::format(kBaseUrl, "id_rev1"),
            cache.GetImageUrl("tag1", 200, "app1", config).value_or(""));
}

UTEST(ImageTagCacheTest, ImageNotFound) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"}, {{"app1", 100}}, std::nullopt, "id1", {{"rev1", "id_rev1"}}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_TRUE(cache.GetImageUrl("tag1", 100, "app1", config).has_value());
  ASSERT_FALSE(cache.GetImageUrl("tag1", 100, "app2", config).has_value());
  ASSERT_FALSE(cache.GetImageUrl("tag2", 100, "app1", config).has_value());
}

UTEST(ImageTagCacheTest, FindNearestSizeByLowerBound) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"}, {{"app1", 100}}, std::nullopt, "id1", {}},
      {{"tag1"}, {{"app1", 200}}, std::nullopt, "id2", {}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_EQ(fmt::format(kBaseUrl, "id1"),
            cache.GetImageUrl("tag1", 100, "app1", config).value_or(""));

  ASSERT_EQ(fmt::format(kBaseUrl, "id2"),
            cache.GetImageUrl("tag1", 150, "app1", config).value_or(""));

  ASSERT_EQ(fmt::format(kBaseUrl, "id2"),
            cache.GetImageUrl("tag1", 200, "app1", config).value_or(""));

  ASSERT_EQ(fmt::format(kBaseUrl, "id2"),
            cache.GetImageUrl("tag1", 250, "app1", config).value_or(""));
}

UTEST(ImageTagCacheTest, ReturnLastRevision) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"},
       {{"app1", 100}},
       std::nullopt,
       "id1",
       {{"rev1", "id_rev1"}, {"rev3", "id_rev3"}, {"rev2", "id_rev2"}}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_EQ(fmt::format(kBaseUrl, "id_rev1"),
            cache.GetImageUrl("tag1:rev1", 100, "app1", config).value_or(""));

  ASSERT_EQ(fmt::format(kBaseUrl, "id_rev2"),
            cache.GetImageUrl("tag1:rev2", 100, "app1", config).value_or(""));

  ASSERT_EQ(fmt::format(kBaseUrl, "id_rev3"),
            cache.GetImageUrl("tag1:rev3", 100, "app1", config).value_or(""));

  ASSERT_EQ(fmt::format(kBaseUrl, "id_rev2"),
            cache.GetImageUrl("tag1", 100, "app1", config).value_or(""));

  ASSERT_EQ(
      fmt::format(kBaseUrl, "id_rev2"),
      cache.GetImageUrl("tag1:<unknown>", 100, "app1", config).value_or(""));
}

UTEST(ImageTagCacheTest, FindTagWithTheme) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"},
       {{"app1", 100}},
       "dark",
       "id1",
       {{"rev1", "id_rev1"}, {"rev3", "id_rev3"}, {"rev2", "id_rev2"}}},
      {{"tag2"}, {{"app1", 200}}, "light", "id2", {{"rev4", "id2_rev4"}}},
      {{"tag2"}, {{"app1", 200}}, "dark", "id3", {{"rev4", "id3_rev4"}}}};

  const auto& cache = ImageTagCache(items);

  // find image by existing theme
  ASSERT_EQ(
      fmt::format(kBaseUrl, "id_rev1"),
      cache.GetImageUrl("tag1:rev1", 100, "app1", config, "dark").value_or(""));

  // find image without theme, return default theme
  ASSERT_EQ(fmt::format(kBaseUrl, "id2_rev4"),
            cache.GetImageUrl("tag2:rev4", 100, "app1", config).value_or(""));

  // find image with unknown theme, return default theme
  ASSERT_EQ(fmt::format(kBaseUrl, "id2_rev4"),
            cache.GetImageUrl("tag2:rev4", 100, "app1", config, "unknown")
                .value_or(""));

  // find image with correct theme
  ASSERT_EQ(
      fmt::format(kBaseUrl, "id3_rev4"),
      cache.GetImageUrl("tag2:rev4", 100, "app1", config, "dark").value_or(""));

  // find image with correct theme, check revision
  ASSERT_EQ(
      fmt::format(kBaseUrl, "id_rev2"),
      cache.GetImageUrl("tag1:rev5", 100, "app1", config, "dark").value_or(""));
}

UTEST(ImageTagCacheTest, FindTagSkipTheme) {
  const auto& config = dynamic_config::GetDefaultSnapshot();
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"},
       {{"app1", 100}},
       std::nullopt,
       "id1",
       {{"rev1", "id_rev1"}, {"rev3", "id_rev3"}, {"rev2", "id_rev2"}}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_EQ(
      fmt::format(kBaseUrl, "id_rev1"),
      cache.GetImageUrl("tag1:rev1", 100, "app1", config, "dark").value_or(""));
}

UTEST(ImageTagCacheTest, CheckExtendTagWithRevision) {
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"},
       {{"app1", 100}},
       std::nullopt,
       "id1",
       {{"rev1", "id_rev1"}, {"rev3", "id_rev3"}, {"rev2", "id_rev2"}}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_EQ(cache.ExtendTagWithRevision("tag1"), "tag1:rev2");
}

UTEST(ImageTagCacheTest, CheckExtendTagMissing) {
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"},
       {{"app1", 100}},
       std::nullopt,
       "id1",
       {{"rev1", "id_rev1"}, {"rev2", "id_rev2"}}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_EQ(cache.ExtendTagWithRevision("tag2"), "tag2");
}

UTEST(ImageTagCacheTest, CheckExtendTagEmptyHistory) {
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"}, {{"app1", 100}}, std::nullopt, "id1", {}}};

  const auto& cache = ImageTagCache(items);

  ASSERT_EQ(cache.ExtendTagWithRevision("tag1"), "tag1:initial");
}

ImageTagCache GetImageTagCacheWithFileFormats() {
  image_tag_cache::models::ImageTagItems items{
      {{"tag1"},
       {{"app1", 100}, {"app1", 200}, {"app2", 100}},
       std::nullopt,
       "tag1_avif",
       {{"rev1", "tag1_avif_rev1"}, {"rev2", "tag1_avif_rev2"}},
       true,
       "avif"},
      {{"tag1"},
       {{"app1", 100}, {"app1", 200}, {"app2", 100}},
       std::nullopt,
       "tag1_default",
       {{"rev1", "tag1_default_rev1"}, {"rev2", "tag1_default_rev2"}},
       true,
       std::nullopt},
      {{"tag1"},
       {{"app1", 100}, {"app1", 200}, {"app2", 100}},
       std::nullopt,
       "tag1_heif_missing_last_revision",
       {
           {"rev1", "tag1_heif_rev1"},
       },
       true,
       "heif"},
      {{"tag2"},
       {{"app1", 100}, {"app1", 200}, {"app2", 100}},
       std::nullopt,
       "tag2_default",
       {{"rev1", "tag2_default_rev1"}, {"rev2", "tag2_default_rev2"}},
       std::nullopt,
       std::nullopt},
      {{"tag3"},
       {{"app1", 100}, {"app1", 200}, {"app2", 100}},
       std::nullopt,
       "tag3_default",
       {{"rev1", "tag3_default_rev1"}, {"rev2", "tag3_default_rev2"}},
       false,
       std::nullopt},
  };
  return ImageTagCache(items);
}

UTEST(ImageTagCacheTest, GetLastRevisionDefaultBecauseNoFormat) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto url = cache.GetImageUrl("tag1", 100, "app1", config);
  ASSERT_EQ(url, fmt::format(kBaseUrl, "tag1_default_rev2"));
}

UTEST(ImageTagCacheTest, GetLastRevisionAvif) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto url =
      cache.GetImageUrl("tag1", 100, "app1", config, std::nullopt, "avif");
  ASSERT_EQ(url, fmt::format(kBaseUrl, "tag1_avif_rev2"));
}

UTEST(ImageTagCacheTest, GetLastRevisionDefaultBecauseLastHeifIsMissing) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto url =
      cache.GetImageUrl("tag1", 100, "app1", config, std::nullopt, "heif");
  ASSERT_EQ(url, fmt::format(kBaseUrl, "tag1_default_rev2"));
}

UTEST(ImageTagCacheTest, GetSpecificRevisionDefault) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto url = cache.GetImageUrl("tag1:rev1", 100, "app1", config);
  ASSERT_EQ(url, fmt::format(kBaseUrl, "tag1_default_rev1"));
}

UTEST(ImageTagCacheTest, GetSpecificRevisionAvif) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto url =
      cache.GetImageUrl("tag1:rev1", 100, "app1", config, std::nullopt, "avif");
  ASSERT_EQ(url, fmt::format(kBaseUrl, "tag1_avif_rev1"));
}

UTEST(ImageTagCacheTest, GetUnknownFileFormat) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto url =
      cache.GetImageUrl("tag1", 100, "app1", config, std::nullopt, "unknown");
  ASSERT_EQ(url, fmt::format(kBaseUrl, "tag1_default_rev2"));
}

UTEST(ImageTagCacheTest, GetUnknownRevision) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto url = cache.GetImageUrl("tag1:unknown", 100, "app1", config,
                               std::nullopt, "avif");
  ASSERT_EQ(url, fmt::format(kBaseUrl, "tag1_avif_rev2"));
}

UTEST(ImageTagCacheTest, GetUnknownRevisionAndFileFormat) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto url = cache.GetImageUrl("tag1:unknown", 100, "app1", config,
                               std::nullopt, "unknown");
  ASSERT_EQ(url, fmt::format(kBaseUrl, "tag1_default_rev2"));
}

UTEST(ImageTagCacheTest, GetIsTintableWithFileFormats) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto tint = cache.GetImageTint("tag1", 100, "app1", config, std::nullopt);
  ASSERT_EQ(tint, true);

  auto tint2 = cache.GetImageTint("tag2", 100, "app1", config, std::nullopt);
  ASSERT_EQ(tint2, std::nullopt);

  auto tint3 = cache.GetImageTint("tag3", 100, "app1", config, std::nullopt);
  ASSERT_EQ(tint3, false);
}

UTEST(ImageTagCacheTest, GetLargestImageWithFileFormats) {
  const auto cache = GetImageTagCacheWithFileFormats();
  const auto& config = dynamic_config::GetDefaultSnapshot();

  auto image = cache.GetLargestImage("tag1", "app1", config);
  ASSERT_TRUE(image.has_value());
  ASSERT_EQ(image->size_hint, 200);
  ASSERT_EQ(image->url, fmt::format(kBaseUrl, "tag1_default_rev2"));
}
