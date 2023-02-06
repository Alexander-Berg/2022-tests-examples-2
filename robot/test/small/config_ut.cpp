#include <library/cpp/resource/resource.h>
#include <library/cpp/json/json_reader.h>
#include <library/cpp/json/json_value.h>
#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>
#include <util/stream/file.h>


Y_UNIT_TEST_SUITE(JsonConfigTest) {
    Y_UNIT_TEST(JsonConfigTest) {
        TString fileString = NResource::Find("config.json");
        TStringInput in(fileString);
        NJson::TJsonValue jsonConfig;
        NJson::ReadJsonTree(&in, &jsonConfig);

        for (const auto& rawRegex : jsonConfig.GetArraySafe()) {
            auto& fullRegex = rawRegex.GetMapSafe();
            TString host = fullRegex.at("host").GetStringSafe();
            TString regex = fullRegex.at("regex").GetStringSafe();
            TString answer = fullRegex.at("answer").GetStringSafe();
            UNIT_ASSERT(answer == "ONE_PRODUCT" || answer == "MANY_PRODUCTS" || answer == "NO_PRODUCTS");
        }

    }
}
