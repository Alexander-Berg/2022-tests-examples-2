#pragma once

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/unittest/tests_data.h>

#include <util/system/env.h>

#include <taxi/logistic-dispatcher/dispatcher/ut/scripts/abstract.h>
#include <taxi/logistic-dispatcher/dispatcher/emulation/emulator.h>
#include <taxi/logistic-dispatcher/dispatcher/planner/planner.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/p2p_allocation/process.h>


using namespace NDispatcherTest;

class TTestConfigGenerator : public TConfigGenerator {
    virtual TString GetHandlersConfig() const {
        TStringStream os;

        TSet<TString> handlersList;
        IRequestProcessorConfig::TFactory::GetRegisteredKeys(handlersList);
        for (auto&& handler : handlersList) {
            os << "<api/" << handler << ">" << Endl;
            os << "AuthModuleName: fake" << Endl;
            os << "ProcessorType: " << handler << Endl;
            os << "</api/" << handler << ">" << Endl;
        }
        return os.Str();
    }
};

class TDispatchTestCase: public NUnitTest::TBaseFixture, public IMessageProcessor {
private:
    CS_ACCESS(TDispatchTestCase, TAtomic, IsActive, 0);
    RTLINE_ACCEPTOR(TDispatchTestCase, P2PAssignRobotActive, bool, false);
    RTLINE_ACCEPTOR(TDispatchTestCase, P2PAssignRobotFrequency, TDuration, TDuration::Seconds(1));
    RTLINE_ACCEPTOR(TDispatchTestCase, PropositionsRobotActive, bool, false);
    RTLINE_ACCEPTOR(TDispatchTestCase, SupplyExperimentRobotActive, bool, true);

    RTLINE_ACCEPTOR(TDispatchTestCase, StateWatcherRobotAction, bool, true);
    RTLINE_ACCEPTOR(TDispatchTestCase, CleanerRobotActive, bool, true);
    RTLINE_ACCEPTOR(TDispatchTestCase, EtaActualizerRobotActive, bool, true);
    RTLINE_ACCEPTOR(TDispatchTestCase, EmployerFactorsRobotActive, bool, true);
    RTLINE_ACCEPTOR(TDispatchTestCase, NeedEmulation, bool, false);
    RTLINE_ACCEPTOR(TDispatchTestCase, CandidatesEmulation, bool, false);
    RTLINE_ACCEPTOR(TDispatchTestCase, LogLevel, ELogPriority, ELogPriority::TLOG_INFO);
    RTLINE_ACCEPTOR(TDispatchTestCase, P2PAssignRobotScript, NLogisticPlanner::TPlannerScript, NLogistic::TP2PAllocationProcess::CreateSimpleP2PScript());
    RTLINE_ACCEPTOR_DEF(TDispatchTestCase, P2PAssignRobotZoneFilter, TString);
    RTLINE_ACCEPTOR(TDispatchTestCase, TaxiConfigClientType, TTaxiConfigClientConfig::EClientType, TTaxiConfigClientConfig::EClientType::Fake);
    RTLINE_ACCEPTOR(TDispatchTestCase, RouterType, TString, "fake");
    RTLINE_ACCEPTOR(TDispatchTestCase, TaxiExternalWaybillPlannerId, TString, "fake_planner");
    RTLINE_ACCEPTOR(TDispatchTestCase, TaxiExternalType, TString, "emulator");
    RTLINE_ACCEPTOR(TDispatchTestCase, S7WaybillPlannerId, TString, "fake_planner");
    RTLINE_ACCEPTOR(TDispatchTestCase, S7OperatorType, TString, "emulator");
    THolder<TDispatcherServerConfig> Config;
    THolder<TDispatcherGuard> Server;
    THolder<TSimpleClient> Client;
    TString DBScheme;
    bool Initialized = false;
    TThreadPool RegularTestThreadPool;
    NRTProc::TAbstractLock::TPtr TestLock;
    void BuildEnv();
    void BuildDatabase(const TDatabasePtr db);
protected:
    virtual void DoRegularTestCheck() const {

    }
public:
    virtual void RegularTestCheck() const final {
        INFO_LOG << LogColorBlue << "CURRENT_SCHEME: " << DBScheme << LogColorNo << Endl;
        DoRegularTestCheck();
    }
    virtual bool Process(IMessage* message) override {
        const TMessageOnAfterDatabaseConstructed* messEvent = dynamic_cast<const TMessageOnAfterDatabaseConstructed*>(message);
        if (messEvent) {
            BuildDatabase(messEvent->GetDatabase("main-db"));
            return true;
        }
        return false;
    }

    virtual TString Name() const override {
        return "TDispatchTestCase";
    }

    TDispatchTestCase() {
        THistoryConfig::DefaultPingPeriod = TDuration::Seconds(3);
        RegisterGlobalMessageProcessor(this);
    }

    ~TDispatchTestCase() {
        AtomicSet(IsActive, 0);
        RegularTestThreadPool.Stop();
        UnregisterGlobalMessageProcessor(this);
    }

    void Initialize();

    TDispatcherGuard& GetServerGuard() {
        return *Server;
    }

    TSimpleClient& GetServerClient() {
        return *Client;
    }

protected:
    using TPatch = TMap<TString, TString>;
    TString PatchRequest(const TString& request, const TPatch& values) {
        TString finalRequest = request;
        for (auto&& [key, value] : values) {
            SubstGlobal(finalRequest, "${" + key + "}", value);
        }
        return finalRequest;
    }

    static TP2PStableRequestGenerator StandartReqGen;
    static TP2PStableRequestGenerator ReturnReqGen;
};
