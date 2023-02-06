#include <robot/blrt/library/perl_ps/perl_process_pool.h>

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/unittest/env.h>
#include <yt/yt/core/concurrency/thread_pool.h>
#include <yt/yt/core/misc/shutdown.h>

using namespace NBlrt;

class TPerlPsTest : public TTestBase {
    UNIT_TEST_SUITE(TPerlPsTest)
        UNIT_TEST(Eviction);
        UNIT_TEST(LongInitialization);
        UNIT_TEST(MultipleNewLines);
        UNIT_TEST(StdInStdOut);
        UNIT_TEST(UnexpectedStdoutEnd);
    UNIT_TEST_SUITE_END();
public:
    explicit TPerlPsTest()
        : ThreadPool(NYT::New<NYT::NConcurrency::TThreadPool>(2, "PerlPsPool"))
    {
    }

    void Eviction() {
        auto ttlEvictionPolicy = MakeIntrusive<TTtlEvictionPolicy>(TDuration::Seconds(1.5));
        auto pool = CreatePerlProcessPool(CreatePerlProcessFactory("eviction_ut.pl"), ttlEvictionPolicy, 1);
        pool->Start();

        {
            auto ps = pool->RentPerlProcess();
            UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "0");
            UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "");
        }

        {
            auto ps = pool->RentPerlProcess();
            UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "1");
            UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "");
        }

        {
            auto ps = pool->RentPerlProcess();
            UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "2");
            UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "");
        }

        {
            auto ps = pool->RentPerlProcess();
            UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "0");
            UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "");
        }
    }

    void LongInitialization() {
        auto pool = CreatePerlProcessPool("long_initialization_ut.pl");

        auto startFuture = BIND([pool]() {
            pool->Start();
        }).AsyncVia(ThreadPool->GetInvoker()).Run();

        UNIT_ASSERT_VALUES_EQUAL(startFuture.Wait(TDuration::Seconds(2)), false);
        UNIT_ASSERT_VALUES_EQUAL(startFuture.Wait(TDuration::Seconds(5)), true);
        UNIT_ASSERT(NYT::NConcurrency::WaitForUnique(startFuture).IsOK());
    }

    void MultipleNewLines() {
        auto pool = CreatePerlProcessPool("multiple_newlines_ut.pl");
        pool->Start();

        auto ps = pool->RentPerlProcess();

        UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "a");
        UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "");

        UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "b");
        UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "c");
        UNIT_ASSERT_VALUES_EQUAL(ps->GetStdOut().ReadLine(), "");
    }

    void StdInStdOut() {
        auto pool = CreatePerlProcessPool("stdin_stdout_ut.pl");
        pool->Start();

        const auto unusedPs = pool->RentPerlProcess();
        auto ps = pool->RentPerlProcess();

        StdInStdOutTestCase0(ps->GetStdIn(), ps->GetStdOut());
        StdInStdOutTestCase1(ps->GetStdIn(), ps->GetStdOut());
    }

    void UnexpectedStdoutEnd() {
        auto pool = CreatePerlProcessPool("unexpected_stdout_end_ut.pl");
        pool->Start();

        auto ps = pool->RentPerlProcess();
        UNIT_ASSERT_EQUAL(ps->GetStdOut().ReadLine(), "abc");
        UNIT_ASSERT_EXCEPTION([&]() {
            while (ps->GetStdOut().ReadLine()) { }
        }(), yexception);
    }

    ~TPerlPsTest() {
        ThreadPool.Reset();
        NYT::Shutdown();
    }
private:
    IPerlProcessFactoryPtr CreatePerlProcessFactory(const TString& perlScript) {
        const auto fullPath = JoinFsPaths(ArcadiaSourceRoot(), "robot/blrt/test/perl_ps_ut", perlScript);
        auto fakeLogger = MakeIntrusive<TPerlStderrLogger>(ThreadPool->GetInvoker());
        fakeLogger->Start();
        return MakeIntrusive<TPerlProcessFactory>(
            MakeIntrusive<TProcessKiller>(FakeCounters),
            fullPath,
            ".",
            TDuration::Seconds(1),
            FakeCounters,
            FakeStatsHistograms.Latency,
            fakeLogger);
    }

    TPerlProcessPoolPtr CreatePerlProcessPool(const TString& perlScript) {
        const auto defaultEvictionPolicy = MakeIntrusive<TTtlEvictionPolicy>(TDuration::Hours(1));
        const auto defaultFactory = CreatePerlProcessFactory(perlScript);
        return CreatePerlProcessPool(defaultFactory, defaultEvictionPolicy, 2);
    }

    TPerlProcessPoolPtr CreatePerlProcessPool(IPerlProcessFactoryPtr factory, IEvictionPolicyPtr evictionPolicy, ui32 poolSize) {
        return MakeIntrusive<TPerlProcessPool>(poolSize, factory, evictionPolicy, ThreadPool->GetInvoker(), TDuration::Seconds(1), FakeCounters);
    }

    void StdInStdOutTestCase0(IOutputStream& stdIn, IInputStream& stdOut) {
        stdIn << "0" << Endl;
        stdIn << "abc" << Endl;
        stdIn << "xyz" << Endl;
        stdIn << Endl;

        UNIT_ASSERT_EQUAL(stdOut.ReadLine(), "Message from perl: abc");
        UNIT_ASSERT_EQUAL(stdOut.ReadLine(), "Message from perl: xyz");
        UNIT_ASSERT_EQUAL(stdOut.ReadLine(), "");
    }

    void StdInStdOutTestCase1(IOutputStream& stdIn, IInputStream& stdOut) {
        stdIn << "1" << Endl << Endl;

        UNIT_ASSERT_EQUAL(stdOut.ReadLine(), "Hello");
        UNIT_ASSERT_EQUAL(stdOut.ReadLine(), "world");
        UNIT_ASSERT_EQUAL(stdOut.ReadLine(), "");
    }
private:
    NYT::NConcurrency::TThreadPoolPtr ThreadPool;
    TPerlProcessCountersPtr FakeCounters = MakeIntrusive<TPerlProcessCounters>(MakeIntrusive<NMonitoring::TDynamicCounters>());
    TStatsHistograms FakeStatsHistograms = TStatsHistograms(NMercury::TStatsConfig());
};

UNIT_TEST_SUITE_REGISTRATION(TPerlPsTest);
