#include "advert_blocks.hpp"

#include <string>
#include <variant>

#include <clients/yabs/client.hpp>

#include <gtest/gtest.h>

namespace handlers::eats_communications_v1_layout_banners::post::blocks {

namespace advert_blocks {

namespace {

using Banner = eats_communications::models::Banner;
using Format = handlers::AdvertSettingsFormat;

std::string GetName(const std::string& src) {
  auto dst = src;
  for (auto it = dst.begin(); it != dst.end(); it++) {
    switch (*it) {
      case ',':
      case '-':
      case ' ':
        *it = '_';
        break;
    }
  }
  return dst;
}

struct AdvertBlockTestCase {
  std::string name;
  handlers::AdvertSettings advert_settings;
  std::vector<Banner> banners;
  std::vector<int64_t> expected_ids;
};

class AdvertBlockTest : public ::testing::TestWithParam<AdvertBlockTestCase> {};

auto WithLimit(size_t limit) {
  return [limit](handlers::AdvertSettings& advert_settings) {
    advert_settings.limit = limit;
  };
}

auto WithIncludeIds(std::unordered_set<int64_t> ids) {
  return [ids = std::move(ids)](AdvertSettings& advert_settings) {
    auto& dst = advert_settings.include_banner_ids.emplace();
    for (const auto id : ids) {
      dst.insert(std::to_string(id));
    }
  };
}

auto WithExcludeIds(std::unordered_set<int64_t> ids) {
  return [ids = std::move(ids)](AdvertSettings& advert_settings) {
    auto& dst = advert_settings.exclude_banner_ids.emplace();
    for (const auto id : ids) {
      dst.insert(std::to_string(id));
    }
  };
}

template <typename... Apply>
handlers::AdvertSettings CreateAdvertSettings(Format format,
                                              Apply... appliers) {
  handlers::AdvertSettings advert_settings;
  advert_settings.format = format;

  (appliers(advert_settings), ...);

  return advert_settings;
}

Banner CreateBanner(int64_t id, Format format) {
  const eats_communications::models::BannerImage kImage{
      "classic.jpeg",  // url
      "light",         // theme
      "web",           // platform
  };

  Banner result;

  result.id = eats_communications::models::BannerId(id);
  switch (format) {
    case Format::kClassic:
      result.images = {kImage};
      break;
    case Format::kShortcut:
      result.shortcuts = {kImage};
      break;
    case Format::kWideAndShort:
      result.wide_and_short = {kImage};
      break;
  }

  return result;
}

std::vector<AdvertBlockTestCase> CreateAdvertBlockTestCases() {
  return {
      {
          "filter by format",                      // name
          CreateAdvertSettings(Format::kClassic),  // advert_settings
          {
              CreateBanner(1, Format::kWideAndShort),
              CreateBanner(2, Format::kClassic),
              CreateBanner(4, Format::kShortcut),
          },    // banners
          {2},  // expected_ids
      },
      {
          "filter by limit",  // name
          CreateAdvertSettings(Format::kClassic,
                               WithLimit(2)),  // advert_settings
          {
              CreateBanner(1, Format::kClassic),
              CreateBanner(2, Format::kClassic),
              CreateBanner(3, Format::kClassic),
          },       // banners
          {1, 2},  // expected_ids
      },
      {
          "filter by include",  // name
          CreateAdvertSettings(Format::kClassic,
                               WithIncludeIds({3})),  // advert_settings
          {
              CreateBanner(1, Format::kClassic),
              CreateBanner(2, Format::kClassic),
              CreateBanner(3, Format::kClassic),
          },    // banners
          {3},  // expected_ids
      },
      {
          "filter by exclude",  // name
          CreateAdvertSettings(Format::kClassic,
                               WithExcludeIds({2})),  // advert_settings
          {
              CreateBanner(1, Format::kClassic),
              CreateBanner(2, Format::kClassic),
              CreateBanner(3, Format::kClassic),
          },       // banners
          {1, 3},  // expected_ids
      },
  };
}

}  // namespace

TEST_P(AdvertBlockTest, Test) {
  const auto param = GetParam();

  AdvertBannersBlock block("test", handlers::BlockType::kAdvert,
                           param.advert_settings, {}, {});
  for (const auto& banner : param.banners) {
    block.Add(banner);
  }

  const auto response_opt = block.Serialize();
  if (param.expected_ids.empty()) {
    ASSERT_FALSE(response_opt.has_value());
    return;
  }

  ASSERT_TRUE(response_opt.has_value());

  const auto& response = response_opt.value();
  const auto& payload = response.payload.As<handlers::AdvertBannersPayload>();

  std::vector<int64_t> actual_ids;
  actual_ids.reserve(payload.advert_banners.size());
  for (const auto& banner : payload.advert_banners) {
    actual_ids.push_back(banner.id);
  }

  ASSERT_EQ(param.expected_ids, actual_ids);
}

INSTANTIATE_TEST_SUITE_P(AdvertBlockTest, AdvertBlockTest,
                         ::testing::ValuesIn(CreateAdvertBlockTestCases()),
                         [](const auto& test_case) {
                           return GetName(test_case.param.name);
                         });

}  // namespace advert_blocks

}  // namespace handlers::eats_communications_v1_layout_banners::post::blocks
