#include "grpc_proxy_client.h"
#include "grpc_proxy_server.h"
#include "metrics.h"
#include "pinger.h"
#include "request.h"
#include "proxy.h"

#include <robot/zora/algo/zlog/zlog.h>
#include <robot/library/utils/signals.h>

#include <library/cpp/getopt/opt.h>
#include <library/cpp/json/json_reader.h>
#include <library/cpp/protobuf/util/pb_io.h>
#include <library/cpp/svnversion/svnversion.h>
#include <util/random/random.h>

#include <ctime>

using namespace NZora;

class TConfig {
public:
    NZoraConfig::TActorSystemConfig ActorSystemConfig;
    ui16 Port;
    ui32 MetricsIntervalMs;

    ui32 NPingers;
    ui32 NPingersDst;
    ui32 NPings;
    ui32 PingIntervalMs;

    ui32 SlowRate;
    ui32 SlowPingIntervalMs;
    ui32 SlowTimeoutMs;

    ui32 FastRate;
    ui32 FastPingIntervalMs;
    ui32 FastTimeoutMs;

    ui32 NSenders;
    ui32 SenderRate;
    ui32 ProxyWaitTime;

    ui32 GrpcPort;
    ui32 NGrpcSenders;
    ui32 GrpcSenderRate;

public:
    TConfig(int argc, const char *argv[]) {
        TString asConfig;

        NLastGetopt::TOpts opts;
        opts.AddLongOption('c', "config", "actorsystem config").Required().StoreResult(&asConfig);
        opts.AddLongOption('p', "port", "monitoring port").Required().StoreResult(&Port);
        opts.AddLongOption("metrics-interval", "metrics interval, ms").StoreResult(&MetricsIntervalMs).DefaultValue("5000");

        opts.AddLongOption("pingers-num", "pingers num").StoreResult(&NPingers).DefaultValue("0");
        opts.AddLongOption("dst-num", "number of pingers where another pinger can send ping").StoreResult(&NPingersDst).DefaultValue("10");
        opts.AddLongOption("pings-num", "pings num").StoreResult(&NPings).DefaultValue("0");
        opts.AddLongOption("pings-interval", "interval bettween two pings, ms. 0 is for direct send").StoreResult(&PingIntervalMs).DefaultValue("1000");

        opts.AddLongOption("slow-rate", "slow requests create rate").StoreResult(&SlowRate).DefaultValue("0");
        opts.AddLongOption("slow-ping-interval", "slow requests ping interval ms").StoreResult(&SlowPingIntervalMs).DefaultValue("11000");
        opts.AddLongOption("slow-timeout", "slow requests ping interval ms").StoreResult(&SlowTimeoutMs).DefaultValue("120000");

        opts.AddLongOption("fast-rate", "fast requests create rate").StoreResult(&FastRate).DefaultValue("0");
        opts.AddLongOption("fast-ping-interval", "fast requests ping interval ms").StoreResult(&FastPingIntervalMs).DefaultValue("290");
        opts.AddLongOption("fast-timeout", "fast requests ping interval ms").StoreResult(&FastTimeoutMs).DefaultValue("3000");

        opts.AddLongOption("senders", "proxy senders num").StoreResult(&NSenders).DefaultValue("0");
        opts.AddLongOption("sender-rate", "proxy senders rate, rps").StoreResult(&SenderRate).DefaultValue("50");
        opts.AddLongOption("wait-time", "proxy wait time, ms").StoreResult(&ProxyWaitTime).DefaultValue("0");

        opts.AddLongOption("grpc-port", "port for grpc").StoreResult(&GrpcPort).DefaultValue("23456");
        opts.AddLongOption("grpc-senders", "grpc proxy senders num (grpc client mode)").StoreResult(&NGrpcSenders).DefaultValue("0");
        opts.AddLongOption("grpc-sender-rate", "grpc proxy senders rate, rps (grpc client mode").StoreResult(&GrpcSenderRate).DefaultValue("50");


        opts.AddHelpOption();
        opts.AddVersionOption();

        NLastGetopt::TOptsParseResult res(&opts, argc, argv);

        ParseFromTextFormat(asConfig, ActorSystemConfig);
    }
};

void CreatePingers(const TConfig& config, const TActorId& metricsAID) {
    TCounters::Get()->NPingers = config.NPingers;
    TCounters::Get()->NPings = config.NPings;

    // creating and starting actors
    TVector<TPinger*> pingers;
    for (ui32 i = 0; i < config.NPingers; ++i) {
        auto pinger = new TPinger(
            metricsAID,
            TDuration::MilliSeconds(config.MetricsIntervalMs),
            TDuration::MilliSeconds(config.PingIntervalMs));
        pingers.emplace_back(pinger);
        TActorSystem::Register(pinger);
    }

    for (auto pinger : pingers) {
        TVector<TActorId> dsts;
        for (size_t i = 0; i < config.NPingersDst; ++i) {
            auto index = RandomNumber<ui32>() % config.NPingers;
            dsts.push_back(pingers[index]->SelfId());
        }
        pinger->SetDst(std::move(dsts));
    }

    for (ui32 i = 0; i < config.NPings; ++i) {
        auto index = RandomNumber<ui32>() % config.NPingers;
        TActorSystem::Send(pingers[index]->SelfId(), MakeHolder<TPinger::TPingEvent>(TInstant::Now()));
    }
}

void CreateRequests(const TConfig& config, const TActorId& metricsAID) {
    TActorSystem::Register(
        new TRequestCreator(
            config.SlowRate,
            metricsAID,
            TDuration::MilliSeconds(config.SlowPingIntervalMs),
            TDuration::MilliSeconds(config.SlowTimeoutMs))
    );

    TActorSystem::Register(
        new TRequestCreator(
            config.FastRate,
            metricsAID,
            TDuration::MilliSeconds(config.FastPingIntervalMs),
            TDuration::MilliSeconds(config.FastTimeoutMs))
    );
}

void CreateProxy(const TConfig& config, const TActorId& metricsAID) {
    auto proxy = TActorSystem::Register(
        new TProxy(
            metricsAID,
            TDuration::MilliSeconds(config.MetricsIntervalMs),
            TDuration::MilliSeconds(config.ProxyWaitTime))
    );

    for (size_t i = 0; i < config.NSenders; ++i) {
        TActorSystem::Register(
            new TSender(
                metricsAID,
                TDuration::MilliSeconds(config.MetricsIntervalMs),
                proxy,
                config.SenderRate
            )
        );
    }
}

void CreateGrpcProxy(const TConfig& config, const TActorId& metricsAID) {
    for (size_t i = 0; i < config.NGrpcSenders; ++i) {
        Cerr << "Create grpc proxy" << Endl;
        auto grpc_proxy = TActorSystem::Register(
            new TGrpcProxyClient(
                metricsAID,
                TDuration::MilliSeconds(config.MetricsIntervalMs),
                TString("zora-actors-tester-")+(rand()%10+1)+".vla.yp-c.yandex.net:"+config.GrpcPort
            )
        );

        TActorSystem::Register(
            new TGrpcSenderClient(
                metricsAID,
                TDuration::MilliSeconds(config.MetricsIntervalMs),
                grpc_proxy,
                config.GrpcSenderRate
            )
        );
    }
}

void CreateGrpcServer(const TConfig& config, const TActorId& metricsAID) {
    Cerr << "Create grpc proxy" << Endl;
    auto grpc_proxy = TActorSystem::Register(
        new TGrpcProxyServer(
            metricsAID,
            TDuration::MilliSeconds(config.MetricsIntervalMs),
            TDuration::MilliSeconds(config.ProxyWaitTime)
        )
    );

    TActorSystem::Register(
        new TGrpcSenderServer(
            TString("0.0.0.0")+config.GrpcPort,
            metricsAID,
            TDuration::MilliSeconds(config.MetricsIntervalMs),
            grpc_proxy
        )
    );
};

int main(int argc, const char* argv[]) {
    NRobot::SetSignalHandlers();
    TConfig config(argc, argv);
    ZLogInfo("config") << config.ActorSystemConfig.DebugString();
    srand(time(0));

    // creating counters
    TAppCounters AppCounters;
    THolder<NRobotCounters::TMonService> MonService;
    MonService.Reset(new NRobotCounters::TMonService(config.Port, "Pinger"));
    AppCounters.Register(MonService.Get());
    MonService->SortPages();
    MonService->Start();

    // creating actorsystem
    TActorSystem::InitStatic(config.ActorSystemConfig);
    TActorSystem::Get()->GetActorSystem().Start();
    TActorSystem::Get()->StartMonitoring();

    auto metricsAID = TActorSystem::Register(new TMetricsHolder);

    CreatePingers(config, metricsAID);
    CreateRequests(config, metricsAID);
    CreateProxy(config, metricsAID);
    CreateGrpcProxy(config, metricsAID);
    CreateGrpcServer(config, metricsAID);



    NRobot::WaitForTerminateSignal();

    // stopping
    TActorSystem::Get()->GetActorSystem().Stop();
    TActorSystem::DestroyStatic();
    MonService->Stop();

    return 0;
}

