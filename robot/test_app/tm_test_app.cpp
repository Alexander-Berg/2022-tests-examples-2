#include "test_app_suites.h"

#include <mapreduce/yt/common/config.h>
#include <mapreduce/yt/library/path_template/path_template_safe.h>
#include <mapreduce/yt/util/ypath_join.h>

#include <robot/jupiter/library/transfer_manager/transfer_table.h>

#include <transfer_manager/cpp/api/multi_task.h>
#include <transfer_manager/cpp/api/proxy.h>
#include <transfer_manager/cpp/api/task.h>
#include <transfer_manager/cpp/api/transfer.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/testing/unittest/registar.h>

#include <util/generic/serialized_enum.h>
#include <util/string/builder.h>

using namespace NTM;
using namespace NTMLibraryTest;
using namespace NJupiter;

struct TApiTestParams {
    TString Cluster1;
    TString Cluster2;
    TString TMHost;
    ui16 TMPort = 0;
    ETMLibraryTestSuite Suite = ETMLibraryTestSuite::TransferTables;
};

TApiTestParams ParseArgs(int argc, char* argv[]) {
    TApiTestParams params;
    NLastGetopt::TOpts parser;

    TVector<NLastGetopt::NComp::TChoice> suiteChoice;
    for (const auto& name: GetEnumAllCppNames<ETMLibraryTestSuite>()) {
        suiteChoice.push_back(name);
    }

    parser.AddLongOption(
            "test-suite",
            (TStringBuilder() << "Test suite. Possible values: " <<  GetEnumAllNames<ETMLibraryTestSuite>()))
        .Required()
        .RequiredArgument("<string>")
        .StoreResultT<ETMLibraryTestSuite>(&params.Suite)
        .Completer(NLastGetopt::NComp::Choice(suiteChoice));

    parser.AddLongOption("tm-host", "Transfer manager host")
        .Required()
        .RequiredArgument("<string>")
        .StoreResult(&params.TMHost);

    parser.AddLongOption("tm-port", "Transfer manager port")
        .Required()
        .RequiredArgument("<ui16>")
        .StoreResult(&params.TMPort);

    TVector<TString> clusters;
    clusters.reserve(2);

    parser.AddLongOption("cluster", "YT cluster")
        .Required()
        .RequiredArgument("<string>")
        .AppendTo(&clusters);

    NLastGetopt::TOptsParseResult parseResults(&parser, argc, argv);
    Y_VERIFY(clusters.size() == 2, "Error: You must pass 2 yt clusters");

    params.Cluster1 = clusters[0];
    params.Cluster2 = clusters[1];

    return params;
}

class TTmTest {
public:
    TTmTest(const TString& cluster1, const TString& cluster2, const TString& tmHost, ui16 tmPort)
        : SourceCluster(NYT::CreateClient(cluster1))
        , DestinationCluster(NYT::CreateClient(cluster2))
        , Proxy(
            NYT::TConfig().Token,
            {tmHost, tmPort, 2, TDuration::Seconds(1)})
    {
        JupiterTransferOpts.TransferManagerHost = tmHost;
        JupiterTransferOpts.TransferManagerPort = tmPort;
        JupiterTransferOpts.TransferManagerRetries = 50;
        JupiterTransferOpts.TmTicketStatusRefreshTime = 1;
        JupiterTransferOpts.MaxSimultaneousTransfers = 2;
    }

    void TestTransfer() const {
        TestCopy();
        TestInterruption();
    }

    void TestTransferDirectory() const {
        const NYT::TYPath root("//Directory");
        SourceCluster->Create(root, NYT::NT_MAP);
        TVector<NYT::TYPath> tables{{"table1", "table2", "table3", "table4"}};

        for (auto& table: tables) {
            table = NYT::JoinYPaths(root, table);
            SourceCluster->Create(table, NYT::NT_FILE);
        }

        TransferDirectory(SourceCluster, root, DestinationCluster, root, JupiterTransferOpts);
        for (const auto& table: tables) {
            UNIT_ASSERT(DestinationCluster->Exists(table));
        }
    }

    void TestSameClusterTransfer() const {
        const NYT::TYPath root("//SameCluster");
        SourceCluster->Create(root, NYT::NT_MAP);
        SourceCluster->Create(NYT::JoinYPaths(root, "string"), NYT::NT_MAP);
        SourceCluster->Create(NYT::JoinYPaths(root, "int"), NYT::NT_UINT64);
        SourceCluster->Create(NYT::JoinYPaths(root, "map"), NYT::NT_MAP);
        SourceCluster->Create(NYT::JoinYPaths(root, "table"), NYT::NT_TABLE);
        SourceCluster->Create(NYT::JoinYPaths(root, "file"), NYT::NT_FILE);
        // ToDo(evseevd): check recursive links in ExpandMultiTask
        //SourceCluster->Link(root, NYT::JoinYPaths(root, "link"));

        const NYT::TYPath destination("//SameClusterDestination");
        TransferDirectory(SourceCluster, root, SourceCluster, destination, JupiterTransferOpts);

        UNIT_ASSERT(SourceCluster->Exists(NYT::JoinYPaths(destination, "table")));
        UNIT_ASSERT(SourceCluster->Exists(NYT::JoinYPaths(destination, "file")));
        UNIT_ASSERT_VALUES_EQUAL(SourceCluster->List(destination).size(), 2);
    }

private:
    void TestCopy() const {
        const NYT::TYPath root("//Copy");
        SourceCluster->Create(root, NYT::NT_MAP);

        TVector<NYT::TYPath> files{{"file1", "file2", "file3", "file4"}};
        TVector<NYT::TYPath> tables{{"table1", "table2", "table3", "table4"}};
        TVector<NYT::TYPath> allTargets;
        allTargets.reserve(files.size() + tables.size());

        for (const auto& file: files) {
            allTargets.push_back(NYT::JoinYPaths(root, file));
            SourceCluster->Create(allTargets.back(), NYT::NT_FILE);
        }
        for (const auto& table: tables) {
            allTargets.push_back(NYT::JoinYPaths(root, table));
            SourceCluster->Create(allTargets.back(), NYT::NT_TABLE);
        }
        for (const auto& target: allTargets) {
            UNIT_ASSERT(SourceCluster->Exists(target));
        }

        auto taskContainer = CreateContainer(allTargets);

        TransferTables(JupiterTransferOpts, taskContainer, false, false);
        for (const auto& target: allTargets) {
            UNIT_ASSERT(DestinationCluster->Exists(target));
        }

        ui64 completed = 0;
        const auto completionCallback = [&completed](bool result) {
            ++completed;
            UNIT_ASSERT(result);
        };

        for (auto& task: taskContainer.Tasks) {
            task.CompletionCallback = completionCallback;
        }

        TransferTables(JupiterTransferOpts, taskContainer, false, true);
        UNIT_ASSERT_VALUES_EQUAL(completed, allTargets.size());
    }

    void TestInterruption() const {
        const NYT::TYPath root("//Interruption");
        SourceCluster->Create(root, NYT::NT_MAP);

        TVector<NYT::TYPath> tables{{"table1", "table2", "table3", "table4"}};
        for (auto& table: tables) {
            table = NYT::JoinYPaths(root, table);
            SourceCluster->Create(table, NYT::NT_TABLE);
        }

        auto transaction = SourceCluster->StartTransaction();
        transaction->Lock(tables[0], NYT::ELockMode::LM_EXCLUSIVE);
        transaction->Lock(tables[1], NYT::ELockMode::LM_EXCLUSIVE);

        ui64 completed = 0;
        const auto callback = [&completed] (bool result) {
            UNIT_ASSERT(result);
            ++completed;
        };

        TMultiTaskContainer taskContainer(SourceCluster, DestinationCluster);
        for (const auto& table: tables){
            taskContainer.AddTask({{table, table}, callback});
        }

        const auto descriptions = ExpandMultiTasks(taskContainer);
        TVector<TTransferTaskId> toWait;
        ui64 counter = 0;
        for (const auto& taskDescription: descriptions.Container()) {
            UNIT_ASSERT_VALUES_EQUAL(taskDescription.Tasks.size(), 1);
            const auto task = Proxy.StartCopying({taskDescription.Tasks.front(), {}});
            if (counter > 1) { // 0 and 1 are locked
                toWait.push_back(task);
            }
            ++counter;
        }

        const auto waitForCallBack = [&](const TTransferTaskId&, const bool result) {
            callback(result);
        };

        WaitForTMTasks(
            Proxy,
            JupiterTransferOpts.TransferManagerRetries,
            TDuration::Seconds(JupiterTransferOpts.TmTicketStatusRefreshTime),
            waitForCallBack,
            toWait);
        UNIT_ASSERT_VALUES_EQUAL(completed, 2);

        transaction->Abort();
        TransferTables(JupiterTransferOpts, taskContainer, true, true);
        UNIT_ASSERT_VALUES_EQUAL(completed, 6);

        for (const auto& table: tables) {
            UNIT_ASSERT(DestinationCluster->Exists(table));
        }
    }

    using TPathsVector = TVector<NYT::TYPath>;
    TMultiTaskContainer CreateContainer(
        const TPathsVector& src,
        std::optional<TPathsVector> dst = {}) const
    {
        TMultiTaskContainer taskContainer(SourceCluster, DestinationCluster);
        if (dst.has_value()) {
            UNIT_ASSERT_VALUES_EQUAL(src.size(), dst.value().size());
            auto srcIt = src.begin();
            auto dstIt = dst.value().begin();
            for (; srcIt != src.end() && dstIt != dst.value().end(); ++srcIt, ++dstIt) {
                taskContainer.AddTask({{*srcIt, *dstIt}});
            }
        } else {
            for (const auto& srcItem: src) {
                taskContainer.AddTask({{srcItem, srcItem}});
            }
        }
        return taskContainer;
    }

private:
    const NYT::IClientPtr SourceCluster;
    const NYT::IClientPtr DestinationCluster;
    const TTransferManagerProxy Proxy;
    TTableTransferOpts JupiterTransferOpts;
};

int main(int argc, char* argv[]) {
    NYT::Initialize(argc, argv);
    const auto params = ParseArgs(argc, argv);

    const TTmTest tmApiTest(params.Cluster1, params.Cluster2, params.TMHost, params.TMPort);
    switch (params.Suite) {
        case ETMLibraryTestSuite::TransferTables:
            tmApiTest.TestTransfer();
            break;
        case ETMLibraryTestSuite::TransferDirectory:
            tmApiTest.TestTransferDirectory();
            break;
        case ETMLibraryTestSuite::SameClusterCopy:
            tmApiTest.TestSameClusterTransfer();
            break;
        default:
            Y_FAIL("Unknown suite %s", ToString(params.Suite).c_str());
            break;
    }
}
