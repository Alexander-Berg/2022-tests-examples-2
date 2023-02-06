#include <robot/saved_copy/client/cpp/lib/rps_shooter/rps_shooter.h>
#include <robot/saved_copy/server/src/lib/connection_pool/proxy_list_retriever.h>
#include <robot/saved_copy/server/src/lib/counters/steady_clock.h>

#include <kernel/yt/logging/log.h>

#include <kernel/yt/utils/yt_utils.h>

#include <mapreduce/yt/interface/client.h>

#include <library/cpp/neh/neh.h>
#include <library/cpp/resource/resource.h>
#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/unittest/tests_data.h>

#include <util/system/env.h>
#include <util/system/hostname.h>
#include <util/system/shellcommand.h>

#include <yaml-cpp/yaml.h>

#include <fstream>
#include <memory>
#include <random>
#include <thread>

using namespace NJupiter;
using namespace NSavedCopy;

class TSavedCopyBackendResponseTest final : public TTestBase {
private:
    using TSelf = TSavedCopyBackendResponseTest;
    UNIT_TEST_SUITE(TSavedCopyBackendResponseTest);
    UNIT_TEST(TestDocsInDb);
    UNIT_TEST(TestDocsNotInDb);
    UNIT_TEST_SUITE_END();

public:
    TSavedCopyBackendResponseTest() {
        YtProxy = GetEnv("YT_PROXY");
        Y_ENSURE(!YtProxy.empty(), "YT_PROXY env varibale must not be empty!");
        ConfigurationPath = PrepareConfigurationFile();
        PrepareUrlLists();
    }

    void SetUp() override {
        L_INFO << "Setting up...";
        RunBackend();
        EventBase = NEvent::CreateEventBase();
        auto dnsBase = NEvent::CreateDnsBase(EventBase.get());
        L_INFO << "Will create connection pool...";
        ConnectionPool = std::make_shared<THttpConnectionPool>(
            EventBase,
            std::move(dnsBase),
            TVector<TEndpoint>{{FQDNHostName(), BackendPort}});
        L_INFO << "The setup finished";
    }

    void TearDown() override {
        L_INFO << "Tearing down...";
        TerminateBackend();
        ConnectionPool.reset();
        EventBase.reset();
        L_INFO << "The tearing down finished";
    }

    void TestDocsInDb() {
        TRpsShooter shooter(
            EventBase,
            ConnectionPool,
            std::make_unique<TContainerAmmoProvider<decltype(DocsInDb)>>(DocsInDb),
            Rps);
        shooter.Start();
        auto results = shooter.GetResults();
        UNIT_ASSERT_VALUES_EQUAL(results[200], DocsInDb.size());
    }

    void TestDocsNotInDb() {
        TRpsShooter shooter(
            EventBase,
            ConnectionPool,
            std::make_unique<TContainerAmmoProvider<decltype(DocsNotInDb)>>(DocsNotInDb),
            Rps);
        shooter.Start();
        auto results = shooter.GetResults();
        UNIT_ASSERT_VALUES_EQUAL(results[404], DocsNotInDb.size());
    }

private:
    bool WaitBackendUp() {
        using namespace NNeh;
        TString url = TStringBuf("http://") + FQDNHostName() + ':' + ToString(BackendPort) + TStringBuf("/ping");
        const auto timeout = std::chrono::seconds(60);
        auto start = TSteadyClock::Now();
        while (TSteadyClock::Now() - start < timeout) {
            TResponseRef resp = Request(url)->Wait(TDuration::MilliSeconds(500));
            if (resp && !resp->IsError()) {
                return true;
            }
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        return false;
    }

    void RunBackend() {
        TShellCommandOptions options{};
        options.SetClearSignalMask(true);
        options.SetCloseAllFdsOnExec(true);
        options.SetAsync(true);
        options.SetLatency(1000); // 1 second
        options.SetUseShell(false);
        options.SetInheritOutput(true);
        options.SetInheritError(true);

        L_INFO << "Will run savedcopyd...";
        Backend.Reset(new TShellCommand(
            BinaryPath("robot/saved_copy/server/src") + "/savedcopyd",
            {"--configuration-path", ConfigurationPath,
             "--signature-key-path", "./test.keys",
             "--stderr-log",
             "--disable-zora-fallback"},
            options));
        Backend->Run();
        auto waitBackendUpSuccess = WaitBackendUp();
        if (waitBackendUpSuccess) {
            L_INFO << "The savedcopyd backend is up!";
        } else {
            L_ERROR << "Failed to wait the savedcopyd backend to get up!";
            Y_FAIL("Failed to wait the savedcopyd backend to get up!");
        }
    }

    void TerminateBackend() {
        Y_VERIFY(Backend);
        Backend->Terminate();
        Backend->Wait();
        const auto exitCode = *Backend->GetExitCode();
        Cerr << "Exit code: " << exitCode;
        Cerr << '\n' << Backend->GetOutput() << '\n';
        Cerr << '\n' << Backend->GetError() << '\n';
    }

    static TDocumentId ParseLine(TStringBuf line) {
        TDocumentId docId;
        TStringBuf url, lat;
        line.RSplit(',', url, lat);
        docId.Url = TString{url};
        docId.LastAccess = FromString<decltype(docId.LastAccess)>(lat);

        return docId;
    }

    static void ReadList(const NYT::IClientBasePtr& client, const NYT::TYPath& listPath, TVector<TDocumentId>* docList) {
        using namespace NYT;
        auto reader = client->CreateFileReader(listPath, TFileReaderOptions{});
        docList->clear();

        TString line;
        size_t length = reader->ReadLine(line);
        while (length != 0) {
            docList->emplace_back(ParseLine(line));
            length = reader->ReadLine(line);
        }
    }

    void PrepareUrlLists() {
        L_INFO << "Will prepare URL lists...";
        auto client = NYT::CreateClient(YtProxy);
        ReadList(client, JoinYtPath(Prefix, "in_db_list"), &DocsInDb);
        ReadList(client, JoinYtPath(Prefix, "not_in_db_list"), &DocsNotInDb);
        std::mt19937 g{};
        std::shuffle(begin(DocsInDb), end(DocsInDb), g);
        std::shuffle(begin(DocsNotInDb), end(DocsNotInDb), g);
        constexpr size_t urlListSizeLimit = 1000u;
        DocsInDb.resize(std::min(urlListSizeLimit, DocsInDb.size()));
        DocsNotInDb.resize(std::min(urlListSizeLimit, DocsNotInDb.size()));
        L_INFO << "The url lists have been prepared";
    }

    TString PrepareConfigurationFile() {
        L_INFO << "Preparing configuration file...";
        using namespace YAML;
        TString filename = "configuration.yaml";
        auto configuration = Load(NResource::Find("/configuration_template").c_str());

        auto location = Node{};
        location["prefix"] = Prefix.c_str();
        location["id"] = "kwyt";
        location["type"] = "static";
        location["shard-count"] = 32;

        auto backend = Node{};
        backend["main-proxy"] = YtProxy.c_str();
        backend["locations"].push_back(std::move(location));

        auto&& backends = configuration["yt-backends"];
        backends.reset();
        backends.push_back(std::move(backend));
        configuration["yt-backends"] = std::move(backends);

        TPortManager pm;
        BackendPort = pm.GetPort(8000);
        configuration["http-listening-port"] = BackendPort;

        configuration["log-file-path"] = static_cast<const TString&>(GetOutputPath() / "savedcopyd.log").c_str();

        std::ofstream keyFile("test.keys", std::ofstream::out);
        keyFile << TestKeys << '\n';
        keyFile.close();

        std::ofstream configurationFile(filename, std::ofstream::out);
        configurationFile << configuration;
        configurationFile.close();

        L_INFO << "The configuration file has been prepared";

        return filename;
    }

private:
    const TString Prefix = "//home/saved-copy";
    const TString TestKeys = "pZlpjKr9UJsCufJ9GgdknW9t4Hw6to9A";
    TString YtProxy;
    TString ConfigurationPath;
    ui16 BackendPort;
    TVector<TDocumentId> DocsInDb;
    TVector<TDocumentId> DocsNotInDb;
    THolder<TShellCommand> Backend;
    std::shared_ptr<event_base> EventBase;
    std::shared_ptr<THttpConnectionPool> ConnectionPool;
    static constexpr size_t Rps = 11;
};

UNIT_TEST_SUITE_REGISTRATION(TSavedCopyBackendResponseTest);
