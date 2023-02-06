#include "util/generic/ptr.h"
#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/unittest/env.h>

#include <robot/blrt/library/perl_ps/perl_process_factory.h>

#include <library/cpp/json/json_reader.h>
#include <library/cpp/json/json_writer.h>

#include <yt/yt/core/misc/shutdown.h>
#include <yt/yt/core/concurrency/thread_pool.h>
#include <util/string/split.h>
#include <util/system/env.h>

using namespace NBlrt;

void CopyMakeBannersMock(const TString& perlLibDir) {
    const auto src = JoinFsPaths(ArcadiaSourceRoot(), "robot/blrt/test/mb_perl_rpc_ut/make_banners_mock.pm");
    const auto dst = JoinFsPaths(perlLibDir, "BM/BannersMaker/MakeBanners.pm");
    TFsPath(src).CopyTo(dst, true);
}

std::pair<ui32, NJson::TJsonValue> ParseOutput(const TString& stdOutLine) {
    auto buf = TStringBuf(stdOutLine);
    ui32 tableIndex = 0;
    NJson::TJsonValue row;
    GetNext(buf, '\t', tableIndex);
    UNIT_ASSERT(NJson::ReadJsonTree(buf, &row, true));
    return {tableIndex, row};
}

void RunPrepareTasksAndOffers(TPerlProcessPtr ps) {
    auto settings = NJson::TJsonMap();
    settings.InsertValue("TASK_TYPE", "perf");
    settings.InsertValue("job_id", "lolkek-1");

    ps->GetStdIn()
        << "prepare_tasks_and_offers" << Endl
        << NJson::WriteJson(settings, false, false, true) << Endl
        << "{\"id\": 1}" << Endl
        << "{\"id\": 3}" << Endl
        << "{\"id\": 4}" << Endl
        << Endl;

    ui32 outputRowIndex = 0;
    const auto expectedRowIds = std::array<ui32, 3>{1, 3, 4};

    while (const auto stdOutLine = ps->GetStdOut().ReadLine()) {
        const auto [tableIndex, row] = ParseOutput(stdOutLine);

        UNIT_ASSERT(outputRowIndex < 4);
        UNIT_ASSERT_EQUAL(tableIndex, 0);
        UNIT_ASSERT_EQUAL(row["row_id"], expectedRowIds[outputRowIndex]);
        UNIT_ASSERT_EQUAL(row["row_count"], outputRowIndex);
        UNIT_ASSERT_EQUAL(row["come_from"], "prepare_tasks_and_offers");
        UNIT_ASSERT_EQUAL(row["test_message_with_nl"], "abc\ndef");

        ++outputRowIndex;
    }
}

void RunProcessOffer(TPerlProcessPtr ps) {
    auto settings = NJson::TJsonMap();
    settings.InsertValue("TASK_TYPE", "perf");
    settings.InsertValue("job_id", "lolkek-2");
    auto stash = NJson::TJsonMap();
    stash.InsertValue("step", 4);
    settings.InsertValue("stash", stash);

    ps->GetStdIn()
        << "process_offer" << Endl
        << NJson::WriteJson(settings, false, false, true) << Endl
        << "{\"id\": 1}" << Endl
        << "{\"id\": 4}" << Endl
        << "{\"id\": 7}" << Endl
        << "{\"id\": 8}" << Endl
        << Endl;

    ui32 outputRowIndex = 0;
    const auto expectedRowIds = std::array<ui32, 4>{1, 4, 7, 8};

    while (const auto stdOutLine = ps->GetStdOut().ReadLine()) {
        const auto [tableIndex, row] = ParseOutput(stdOutLine);

        UNIT_ASSERT(outputRowIndex < 5);
        if (outputRowIndex < 4) {
            UNIT_ASSERT_EQUAL(tableIndex, 2);
            UNIT_ASSERT_EQUAL(row["row_id"], expectedRowIds[outputRowIndex]);
            UNIT_ASSERT_EQUAL(row["stash_data"], 4);
            UNIT_ASSERT_EQUAL(row["come_from"], "process_offer");
        } else {
            UNIT_ASSERT_EQUAL(tableIndex, 4);
            UNIT_ASSERT_EQUAL(row["message"], "log\tmessage");
        }

        ++outputRowIndex;
    }
}

Y_UNIT_TEST_SUITE(MakeBannersPerlRpcTests) {

    Y_UNIT_TEST(MakeBannersPerlRpcTest) {
        const auto blrtScriptPath = JoinFsPaths(BuildRoot(), "robot/blrt/packages/worker_configs/blrt.pl");
        const auto perlLibDir = JoinFsPaths(GetWorkPath(), "perl_lib");
        CopyMakeBannersMock(perlLibDir);

        {
            const auto backgroundThreadPool = NYT::New<NYT::NConcurrency::TThreadPool>(1, "BlrtTestBackgroud");
            auto fakeCounters = MakeIntrusive<TPerlProcessCounters>(MakeIntrusive<NMonitoring::TDynamicCounters>());
            auto fakeLogger = MakeIntrusive<TPerlStderrLogger>(backgroundThreadPool->GetInvoker());
            fakeLogger->Start();
            auto ps = TPerlProcessFactory(
                MakeIntrusive<TProcessKiller>(fakeCounters),
                blrtScriptPath,
                perlLibDir,
                TDuration::Seconds(1),
                fakeCounters,
                TStatsHistograms(NMercury::TStatsConfig()).Latency,
                fakeLogger
            ).Spawn();

            RunPrepareTasksAndOffers(ps);
            RunPrepareTasksAndOffers(ps);
            RunProcessOffer(ps);
        }

        NYT::Shutdown();
    }
}
