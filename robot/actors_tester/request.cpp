#include "activities.h"
#include "request.h"

TRequest::TRequest(TActorId metricsAID, TDuration pingDelay, TDuration killDelay)
    : PingDelay(pingDelay)
    , KillDelay(killDelay)
    , MetricsAID(metricsAID)
{
    SetActivityType(AT_REQUEST);
    AddHandler(&TRequest::OnPing);
    AddHandler(&TRequest::OnKill);
}

void TRequest::OnAfterRegister() {
    Schedule(PingDelay, new TPingEvent(TInstant::Now() + PingDelay));
    Schedule(KillDelay, new TKillEvent());
}

void TRequest::OnPing(TPingEvent& event) {
    auto now = TInstant::Now();
    if (now > event.ApproxDeliveryTime) {
        Metrics.Add(now - event.ApproxDeliveryTime);
    } else {
        Metrics.Add(TDuration::Zero());
    }

    Schedule(PingDelay, new TPingEvent(TInstant::Now() + PingDelay));
}

void TRequest::OnKill(TKillEvent& event) {
    Y_UNUSED(event);
    Metrics.Count += 2;
    Send(MetricsAID, new TMetricsHolder::TMetricsEvent(Metrics));
    PassAway();
}



TRequestCreator::TRequestCreator(ui32 rate, TActorId metricsAID, TDuration pingDelay, TDuration killDelay)
    : Rate(rate)
    , MetricsAID(metricsAID)
    , PingDelay(pingDelay)
    , KillDelay(killDelay)
{
    SetActivityType(AT_REQUEST);
    AddHandler(&TRequestCreator::OnWakeUp);
}

void TRequestCreator::OnAfterRegister() {
    Schedule(TDuration::Seconds(1), new TWakeUp());
}

void TRequestCreator::OnWakeUp(TWakeUp& event) {
    Y_UNUSED(event);
    for (size_t i = 0; i < Rate; ++i) {
        auto request = new TRequest(MetricsAID, PingDelay, KillDelay);
        TActorSystem::Register(request);
    }
    Schedule(TDuration::Seconds(1), new TWakeUp());
}
