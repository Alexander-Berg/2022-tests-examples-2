#pragma once

#include <functional>

#include <library/cpp/json/writer/json_value.h>

#define TESTPOINT(name, json) TESTPOINT_CALLBACK(name, json, {})
#define TESTPOINT_CALLBACK(name, json, callback)                             \
  do {                                                                       \
    if (!::testsuite::IsTestpointEnabled()) break;                           \
    ::testsuite::Testpoint(name, json, callback);                            \
  } while (0)

namespace testsuite {
    bool IsTestpointEnabled();
    void Testpoint(const TString& name, const NJson::TJsonValue& json,
                   const std::function<void(const NJson::TJsonValue&)>& callback = {});
}
