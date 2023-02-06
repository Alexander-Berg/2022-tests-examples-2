#pragma once

#include <set>
#include <vector>

#include <subvention_matcher/types.hpp>

#include "common.hpp"

using namespace subvention_matcher;

inline DriverPropertyMap BuildDPM() {
  DriverPropertyMap dpm;

  // zone
  dpm[PropertyType::kZone] = {ZoneProperty{{"moscow"}}, PropertySource::kFake};

  // class
  dpm[PropertyType::kClass] = {ClassProperty{{"econom"}},
                               PropertySource::kFake};

  // branding
  dpm[PropertyType::kBranding] = {BrandingProperty{{false, false}},
                                  PropertySource::kFake};

  // activity
  dpm[PropertyType::kActivity] = {ActivityProperty{{100}},
                                  PropertySource::kFake};

  // tags
  dpm[PropertyType::kTags] = {TagsProperty{{std::set<std::string>{"tag"}}},
                              PropertySource::kFake};

  return dpm;
}

inline std::set<KeyPoint> BuildKeypoints(int keypoints_size) {
  std::set<KeyPoint> keypoints;
  for (int i = 0; i < keypoints_size; i++) {
    keypoints.insert(
        std::chrono::system_clock::time_point(std::chrono::seconds(i)));
  }

  return keypoints;
}

inline std::vector<DriverPropertyMap> BuildProperties(int properties_size) {
  std::vector<DriverPropertyMap> properties;
  for (int i = 0; i < properties_size; i++) {
    properties.push_back(BuildDPM());
  }

  return properties;
}
