#pragma once

#include <userver/testsuite/testpoint.hpp>

#define JS_PIPELINE_TESTPOINT(activity) \
  TESTPOINT("js-pipeline", [] {         \
    formats::json::ValueBuilder json;   \
    json["activity"] = activity;        \
    return json.ExtractValue();         \
  }())
