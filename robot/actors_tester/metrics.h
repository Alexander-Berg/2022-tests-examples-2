#pragma once

#include <robot/zora/algo/actors/base.h>
#include <robot/zora/tools/actors_tester/proto/counters.pb.h>

#include <robot/library/counters/dynamic_counters/counters.h>

using namespace NZora;

class TMetrics {
public:
    TMetrics();

    static constexpr ui32 mks = 1;
    static constexpr ui32 ms = 1000;
    static constexpr ui32 s = 1000 * 1000;
    static constexpr std::array<ui32, 16> Borders = {
        100*mks, 200*mks, 500*mks,
        1*ms, 2*ms, 5*ms,
        10*ms, 20*ms, 50*ms,
        100*ms, 200*ms, 500*ms,
        1*s, 2*s, 5*s,
        static_cast<ui32>(-1)};

    TVector<ui32> Metrics;
    ui32 Count;

    ui32 InFly;
    ui32 InFlySender;

public:
    void Add(TDuration item);
    void Add(const TMetrics& other);
    void Clear();
};


class TMetricsHolder : public TSimpleActor {
public:
    class TMetricsEvent;
    class TWakeUpEvent : public TEvent<TWakeUpEvent> {};

    TMetricsHolder();

    void OnAfterRegister() override;

    void OnMetrics(TMetricsEvent& event);
    void OnWakeUp(TWakeUpEvent& event);

private:
    TMetrics Metrics;
    THashMap<ui32, ui32> InFly;
};

class TMetricsHolder::TMetricsEvent : public TEvent<TMetricsHolder::TMetricsEvent> {
public:
    TMetricsEvent(const TMetrics& metrics)
        : Metrics(metrics)
    {}

    TMetrics Metrics;
};


// solomon counters stuff
class TCounters : public NRobotCounters::TComponentCountersBase<TCounters> {
public:
    using TBase = NRobotCounters::TComponentCountersBase<TCounters>;
    using TProto = NPingerCounters::TPingerCounters;


    TCounters() : TBase("Base") {
        PingTimings.assign(TMetrics::Borders.size(), 0);
    }
    void ToProto(TProto* counters);
    using TBase::ToProto;

public:
    NRobotCounters::TCounter NPingers;
    NRobotCounters::TCounter NPings;

    NRobotCounters::TCounter ProcessedPings;
    NRobotCounters::TCounter NotAnsweredProxyPings;
    TVector<NRobotCounters::TCounter> PingTimings;
};


class TAppCounters : public NRobotCounters::IAppCounters {
public:
    TAppCounters(const IAppCounters::TLabels& labels = {})
        : NRobotCounters::IAppCounters("Pinger", labels)
    {}

    void RegisterInner(NRobotCounters::TMonService* monService) const override final;
    THolder<google::protobuf::Message> AsProto() override;
};

