#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/resource/resource.h>

#include <util/stream/file.h>
#include <util/folder/path.h>

#include "smart_devices/crash_analytics/tools/s3_minidump_stackwalk/engine/s3_minidump_stackwalk_engine.h"

#include <iostream>

using namespace yandex_io_breakpad;
using namespace google_breakpad;

namespace {
    struct Fixture: public NUnitTest::TBaseFixture {
        std::string symbolsUrl;

        Fixture() {
            TString tmpDir = getenv("TMPDIR");
            if (!tmpDir.empty()) {
                TFsPath fsPath = TFsPath(tmpDir) / "symbols_url.txt";
                TFile symbolsUrlFile(fsPath, RdOnly | AR);
                TFileInput in(symbolsUrlFile);
                symbolsUrl = in.ReadAll();
            } else {
                // suppose we're in debug mode, make  sure we can proceed
                symbolsUrl = "http://s3.mds.yandex.net/quasar-symbols";
            }
        }
    };
} // namespace

Y_UNIT_TEST_SUITE_F(Breakpad, Fixture) {
    Y_UNIT_TEST(ParseTest) {

        const std::string GOOD_64_10_REQUESTING_THREAD = "\n31|0|libc.so||||0x21be4\n31|1|libc.so||||0x21bb8\n31|2|maind|quasar::MediaEndpoint::processQuasarMessage(quasar::proto::QuasarMessage const&)|/-S/yandex_io/services/mediad/MediaEndpoint.cc|553|0x0\n31|3|maind|void auto quasar::makeSafeCallback<std::__y1::function<void ()> >(std::__y1::function<void ()>, quasar::Lifetime::Tracker)::'lambda'(auto&&...)::operator()<>(auto&&...) const|/-S/contrib/libs/cxxsupp/libcxx/include/functional|2478|0x4\n";
        const std::string GOOD_71_20_REQUESTING_THREAD_1 = "\n0|0|libc.so||||0x21be4\n0|1|libc.so||||0x21bb8\n0|2|maind|abort_message|/buildbot/src/android/ndk-release-r22/toolchain/llvm-project/libcxx/../../../toolchain/llvm-project/libcxxabi/src/abort_message.cpp|76|0x0\n0|3|maind|google_breakpad::ExceptionTrap::terminate() const|/-S/contrib/libs/breakpad/src/client/linux/handler/exception_trap.cc|59|0x0\n";
        const std::string GOOD_71_20_REQUESTING_THREAD_2 = "\n0|0|libc.so||||0x21be4\n0|1|libc.so||||0x21bb8\n0|2|maind|abort_message|/buildbot/src/android/ndk-release-r22/toolchain/llvm-project/libcxx/../../../toolchain/llvm-project/libcxxabi/src/abort_message.cpp|76|0x0\n0|3|maind|google_breakpad::ExceptionTrap::terminate() const|/-S/contrib/libs/breakpad/src/client/linux/handler/exception_trap.cc|59|0x0\n";

        S3MinidumpStackwalkEngine engine(symbolsUrl);
        Options options;
        options.stream_mode = true;

        {
            auto dmpstr = NResource::Find("good.71-20.1.dmp");
            std::stringstream ss(dmpstr);
            options.minidump_stream = std::move(ss);

            auto response = engine.ParseMinidump(options);

            UNIT_ASSERT_VALUES_EQUAL(true, response.has_parse_response());
            UNIT_ASSERT_VALUES_EQUAL(response.parse_response().requesting_thread(), GOOD_71_20_REQUESTING_THREAD_1);
            UNIT_ASSERT_VALUES_EQUAL(response.parse_response().crash_reason(), "SIGABRT");
        }

        {
            auto dmpstr = NResource::Find("good.64-10.dmp");
            std::stringstream ss(dmpstr);
            options.minidump_stream = std::move(ss);

            auto response = engine.ParseMinidump(options);

            UNIT_ASSERT_VALUES_EQUAL(true, response.has_parse_response());
            UNIT_ASSERT_VALUES_EQUAL(response.parse_response().requesting_thread(), GOOD_64_10_REQUESTING_THREAD);
            UNIT_ASSERT_VALUES_EQUAL(response.parse_response().crash_reason(), "SIGABRT");
        }

        {
            auto dmpstr = NResource::Find("good.71-20.2.dmp");
            std::stringstream ss(dmpstr);
            options.minidump_stream = std::move(ss);

            auto response = engine.ParseMinidump(options);

            UNIT_ASSERT_VALUES_EQUAL(true, response.has_parse_response());
            UNIT_ASSERT_VALUES_EQUAL(response.parse_response().requesting_thread(), GOOD_71_20_REQUESTING_THREAD_2);
            UNIT_ASSERT_VALUES_EQUAL(response.parse_response().crash_reason(), "SIGABRT");
        }
    }

    Y_UNIT_TEST(ParseCorruptedMinidumpTest) {
        S3MinidumpStackwalkEngine engine(symbolsUrl);
        Options options;
        options.stream_mode = true;

        {
            auto dmpstr = NResource::Find("bad.dmp");
            std::stringstream ss(dmpstr);
            options.minidump_stream = std::move(ss);

            auto response = engine.ParseMinidump(options);

            UNIT_ASSERT_VALUES_EQUAL(true, response.has_error_response());
            UNIT_ASSERT_EQUAL(s3_minidump_stackwalk::proto::ErrorResponse_ErrorCode_NO_THREAD_LIST, response.error_response().error_code());
        }
    }

    Y_UNIT_TEST(ParseBadHeaderMinidumpTest) {
        S3MinidumpStackwalkEngine engine(symbolsUrl);
        Options options;
        options.stream_mode = true;

        {
            auto dmpstr = NResource::Find("bad-header.dmp");
            std::stringstream ss(dmpstr);
            options.minidump_stream = std::move(ss);

            auto response = engine.ParseMinidump(options);

            UNIT_ASSERT_VALUES_EQUAL(true, response.has_error_response());
            UNIT_ASSERT_EQUAL(s3_minidump_stackwalk::proto::ErrorResponse_ErrorCode_MINIDUMP_COULD_NOT_BE_READ, response.error_response().error_code());
        }
    }

    Y_UNIT_TEST(HandleEofTest) {
        S3MinidumpStackwalkEngine engine(symbolsUrl);
        Options options;
        options.stream_mode = true;
        TStringStream sIn;
        TStringStream sOut;
        engine.Process(options, sIn, sOut);

        size_t size;
        sOut.Load(&size, sizeof(size));
        TVector<char> buffer;
        buffer.resize(size);

        sOut.Load(buffer.data(), size);
        s3_minidump_stackwalk::proto::Response response;
        Y_PROTOBUF_SUPPRESS_NODISCARD response.ParseFromArray(buffer.data(), size);

        UNIT_ASSERT_VALUES_EQUAL(true, response.has_error_response());
        UNIT_ASSERT_EQUAL(s3_minidump_stackwalk::proto::ErrorResponse_ErrorCode_MINIDUMP_COULD_NOT_BE_READ, response.error_response().error_code());
    }
}
