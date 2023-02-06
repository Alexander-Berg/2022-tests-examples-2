#include <smart_devices/tools/launcher2/lib/task.h>

#include <library/cpp/testing/unittest/registar.h>

Y_UNIT_TEST_SUITE(TLoadConfig) {
    Y_UNIT_TEST(Smoke) {
        const std::string json("{\"name\": \"heapy\", \"delay\" : 10, \"allowedRestartIntervalSeconds\" : 20, \"arg\": [\"a1\", \"a2\"] ,"
                               "\"root\": \".\", \"path\": \"testPath\",\"log\": true,\"ldLibraryPrefix\":\"/libs\"}");
        std::stringstream jsonStream(json);
        Json::CharReaderBuilder builder;
        Json::Value root;
        builder["collectComments"] = false;
        JSONCPP_STRING errs;
        UNIT_ASSERT(parseFromStream(builder, jsonStream, &root, &errs));
        const auto params = taskParamsFromJson(root);
        UNIT_ASSERT_EQUAL(params.name, "heapy");
        UNIT_ASSERT_EQUAL(params.path, "testPath");
        UNIT_ASSERT_EQUAL(params.root, ".");
        UNIT_ASSERT_EQUAL(params.log, true);
        UNIT_ASSERT_EQUAL(params.delay, 10);
        UNIT_ASSERT_EQUAL(params.allowedRestartInterval, std::chrono::milliseconds(20000));
        UNIT_ASSERT_EQUAL(params.ldLibraryPrefix, "/libs");
        UNIT_ASSERT_EQUAL(params.args.size(), 2);
        UNIT_ASSERT_EQUAL(params.args[0], "a1");
        UNIT_ASSERT_EQUAL(params.args[1], "a2");
    }
}
