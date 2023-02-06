#include <robot/zora/gozora/internal/cfg_proto/cfg.pb.h>

#include <library/cpp/protobuf/util/pb_io.h>
#include <library/cpp/testing/common/env.h>
#include <library/cpp/testing/unittest/registar.h>

#include <iostream>

using namespace NZora;

class TGozoraClientsTest : public TTestBase {
    UNIT_TEST_SUITE(TGozoraClientsTest)
    UNIT_TEST(TestAll)
    UNIT_TEST_SUITE_END();

protected:
    void TestAll();

    void TestTvmDups();
};

UNIT_TEST_SUITE_REGISTRATION(TGozoraClientsTest)


void TGozoraClientsTest::TestAll() {
    TestTvmDups();
}

void TGozoraClientsTest::TestTvmDups() {
    ClientConfiguration config;
    ParseFromTextFormat(ArcadiaSourceRoot() + "/robot/zora/gozora/conf/common/clients.pb.txt", config);

    THashMap<ui32, TVector<TString>> tvmToSources;
    THashSet<TString> allowedSources;
    THashSet<TString> sources;

    for (const auto& client : config.GetClients()) {
        auto name = client.GetName();

        UNIT_ASSERT_C(!sources.contains(name), "Duplicate source: " + name);
        sources.insert(name);

        if (client.GetCanUseMultiTvms()) {
            allowedSources.insert(name);
        }
        for (const auto& tvm : client.GetTvmId()) {
            tvmToSources[tvm].push_back(name);
        }
    }

    bool hasErrors = false;
    for (const auto& item : tvmToSources) {
        if (item.second.size() < 2) {
            continue;
        }

        auto tvm = item.first;
        TString clients = "";
        bool isError = false;
        for (const auto& client : item.second) {
            if (!allowedSources.contains(client)) {
                isError = true;
            }
            clients = clients + client + " ";
        }

        if (isError) {
            hasErrors = true;
            std::cerr << "One tvm in multiple clients whtiout CanUseMultiTvms; tvm: " << tvm << "; clients: " << clients << "\n";
        }
    }
    UNIT_ASSERT_C(!hasErrors, "Some tvms in multiple clients whtiout CanUseMultiTvms; see stderr for details");
}
