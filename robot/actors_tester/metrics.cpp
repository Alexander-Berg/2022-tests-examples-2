#include "metrics.h"

#include <robot/library/actors/counters.h>
#include <robot/zora/algo/zlog/zlog.h>

TMetricsHolder::TMetricsHolder() {
    AddHandler(&TMetricsHolder::OnMetrics);
    AddHandler(&TMetricsHolder::OnWakeUp);
}

void TMetricsHolder::OnAfterRegister() {
    Schedule(TDuration::Seconds(2), new TWakeUpEvent);
}

void TMetricsHolder::OnMetrics(TMetricsEvent& event) {
    Metrics.Add(event.Metrics);
    InFly[event.Metrics.InFlySender] = event.Metrics.InFly;
}

void TMetricsHolder::OnWakeUp(TWakeUpEvent& event) {
    Y_UNUSED(event);
    TCounters::Get()->ProcessedPings = Metrics.Count;
    for (size_t i = 0; i < Metrics.Metrics.size(); ++i) {
        TCounters::Get()->PingTimings[i] = Metrics.Metrics[i];
    }

    ui32 inFly = 0;
    for (auto item : InFly) {
        inFly += item.second;
    }
    TCounters::Get()->NotAnsweredProxyPings = inFly;

    Schedule(TDuration::Seconds(2), new TWakeUpEvent);
}


TMetrics::TMetrics()
    : InFlySender(static_cast<ui32>(-1))
{
    Clear();
}

void TMetrics::Add(TDuration item) {
    ui32 mks = item.MicroSeconds();
    for (size_t i = 0; i < Borders.size(); ++i) {
        if (mks < Borders[i]) {
            ++Metrics[i];
            break;
        }
    }
    ++Count;
}

void TMetrics::Add(const TMetrics& other) {
    for (size_t i = 0; i < Borders.size(); ++i) {
        Metrics[i] += other.Metrics[i];
    }
    Count += other.Count;
}

void TMetrics::Clear() {
    Count = 0;
    InFly = 0;
    Metrics.assign(Borders.size(), 0);
}


void TCounters::ToProto(TProto* counters) {
    counters->SetNPingers(NPingers);
    counters->SetNPings(NPings);
    counters->SetProcessedPings(ProcessedPings);
    counters->SetNotAnsweredProxyPings(NotAnsweredProxyPings);
    for (size_t i = 0; i < PingTimings.size(); ++i) {
        auto group = counters->AddPingTimingsMks();
        group->SetName(ToString<ui32>(TMetrics::Borders[i]));
        group->SetCount(PingTimings[i]);
    }
}


void TAppCounters::RegisterInner(NRobotCounters::TMonService* monService) const {
    RegisterInnerComponent(TCounters::Get(), monService);
    RegisterInnerComponent(NRobot::TActorSystemCounters::Get(), monService);
}

THolder<google::protobuf::Message> TAppCounters::AsProto() {
    auto counters = MakeHolder<NPingerCounters::TPingerAppCounters>();

    FillCommonDaemonAppFields(*counters);

    counters->MutableCounters()->MutablePingerCounters()->MergeFrom(*TCounters::Get()->ToProto());
    counters->MutableCounters()->MutableActorSystem()->MergeFrom(*NRobot::TActorSystemCounters::Get()->ToProto());
    return counters;
}
