#include <smart_devices/tools/updater/tests/lib/base_fixture.h>
#include <smart_devices/tools/updater/tests/lib/http_server.h>
#include <smart_devices/tools/updater/tests/lib/utils.h>
#include <smart_devices/tools/updater/lib/http_client.h>
#include <smart_devices/tools/updater/lib/utils.h>

#include <library/cpp/testing/unittest/env.h>

#include <fstream>
#include <utility>

using namespace IOUpdater;

namespace {

    class Fixture: public BaseFixture {
    public:
        Fixture() {
            updateData_ =
                "This is the long content aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

            mockBackend_.addHandler("/get", []() {
                THttpResponse resp;
                const TString respStr{"This is a get response"};
                resp.SetContent(respStr, "text/html");
                return resp;
            });

            mockBackend_.addHandler("/download/ota.zip", [this] {
                //const auto code = failDownload_.load() ? HTTP_INTERNAL_SERVER_ERROR : HTTP_OK;
                THttpResponse resp;
                if (!firstRequestDone_.load()) {
                    resp.SetHttpCode(HTTP_OK);
                    resp.SetContent(TString{updateData_.begin(), updateData_.begin() + updateData_.length() / 2}, "text/html");
                    firstRequestDone_.store(true);
                } else if (!secondRequestDone_.load()) {
                    resp.SetHttpCode(HTTP_PARTIAL_CONTENT);
                    resp.AddHeader({"Content-Range", "64-127/128"});
                    resp.SetContent(TString{updateData_.begin() + updateData_.length() / 2, updateData_.end()}, "text/html");
                    secondRequestDone_.store(true);
                } else if (!thirdRequestDone_.load()) {
                    resp.SetHttpCode(HTTP_REQUESTED_RANGE_NOT_SATISFIABLE);
                    resp.SetContent(TString{updateData_}, "text/html");
                    thirdRequestDone_.store(true);
                } else {
                    UNIT_FAIL("More than three requests done, that's not expected");
                }

                return resp;
            });
        };

    protected:
        std::mutex mutex_;
        std::condition_variable cv_;
        std::atomic_bool failDownload_{false};
        TestHTTPServer mockBackend_;
        std::string updateData_{};
        std::atomic<bool> firstRequestDone_{false};
        std::atomic<bool> secondRequestDone_{false};
        std::atomic<bool> thirdRequestDone_{false};
    };

    Y_UNIT_TEST_SUITE_F(TestHttpClient, Fixture) {
        Y_UNIT_TEST(testDownloadResume) {
            HttpClient client{""};
            auto result = client.download(mockBackend_.address() + "/download/ota.zip", GetWorkPath(), "ota.zip", nullptr);
            UNIT_ASSERT_UNEQUAL(result, std::nullopt);
            result = client.download(mockBackend_.address() + "/download/ota.zip", GetWorkPath(), "ota.zip", nullptr);
            UNIT_ASSERT_UNEQUAL(result, std::nullopt);
            // Trying to download existing file again should not fail and client should not try to delete/overwrite it
            result = client.download(mockBackend_.address() + "/download/ota.zip", GetWorkPath(), "ota.zip", nullptr);
            UNIT_ASSERT_UNEQUAL(result, std::nullopt);

            std::ifstream in(*result, std::ios::binary);
            std::ostringstream contents;
            contents << in.rdbuf();
            UNIT_ASSERT_EQUAL(contents.str(), updateData_);
        }
    }

} // namespace
