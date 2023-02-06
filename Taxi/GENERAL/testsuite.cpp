#include "testsuite.h"

#include <taxi/logistic-dispatcher/util/testpoint.h>

namespace testsuite {
    namespace {
        const TTestsuiteClient *testsuiteClient = nullptr;
    }

    void EnableTestpoint(const TTestsuiteClient *client) {
        testsuiteClient = client;
    }

    void DisableTestpoint() {
        testsuiteClient = nullptr;
    }

    bool IsTestpointEnabled() {
        return testsuiteClient != nullptr;
    }

    void Testpoint(const TString& name, const NJson::TJsonValue& json,
                   const std::function<void(const NJson::TJsonValue&)>& callback) {
        if (!IsTestpointEnabled())
            return;
        auto result = testsuiteClient->Testpoint(name, json);
        if (callback) {
            callback(result);
        }
    }
}
