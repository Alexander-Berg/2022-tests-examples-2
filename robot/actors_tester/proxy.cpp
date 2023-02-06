#include "activities.h"
#include "proxy.h"

#include <robot/zora/algo/zlog/zlog.h>

TProxy::TProxy(TActorId metricsAID, TDuration metricsDelay, TDuration waitTime)
    : WaitTime(waitTime)
    , MetricsAID(metricsAID)
    , MetricsDelay(metricsDelay)
{
    SetActivityType(AT_PROXY);
    AddHandler(&TProxy::OnPing);
    AddHandler(&TProxy::OnMetricsSchedule);
}

void TProxy::OnAfterRegister() {
    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}

void TProxy::OnPing(TPingEvent& event) {
    auto now = TInstant::Now();
    if (now > event.ApproxDeliveryTime) {
        Metrics.Add(now - event.ApproxDeliveryTime);
    } else {
        Metrics.Add(TDuration::Zero());
    }

    if (WaitTime != TDuration::Zero()) {
        Sleep(WaitTime);
    }

    Send(event.Sender, new TPongEvent(TInstant::Now()));
}

void TProxy::OnMetricsSchedule(TMetricsScheduleEvent& event) {
    Y_UNUSED(event);
    Metrics.Count += 2;
    Send(MetricsAID, new TMetricsHolder::TMetricsEvent(Metrics));
    Metrics.Clear();

    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}


static ui32 SenderIdGenerator = 0;

TSender::TSender(TActorId metricsAID, TDuration metricsDelay, TActorId proxyAID, ui32 rate)
    : Proxy(proxyAID)
    , Rate(rate)
    , InFly(0)
    , SenderId(++SenderIdGenerator)
    , MetricsAID(metricsAID)
    , MetricsDelay(metricsDelay)
{
    SetActivityType(AT_PROXY);
    AddHandler(&TSender::OnPong);
    AddHandler(&TSender::OnSend);
    AddHandler(&TSender::OnMetricsSchedule);
}

void TSender::OnAfterRegister() {
    Schedule(MetricsDelay, new TMetricsScheduleEvent);
    Schedule(TDuration::Seconds(1), new TSendEvent);
}

void TSender::OnSend(TSendEvent& event) {
    Y_UNUSED(event);
    InFly += Rate;
    auto now = TInstant::Now();
    for (size_t i = 0; i < Rate; ++i) {
        Send(Proxy, new TProxy::TPingEvent(now, SelfId()));
    }
    Schedule(TDuration::Seconds(1), new TSendEvent);
}

void TSender::OnPong(TProxy::TPongEvent& event) {
    Y_UNUSED(event);
    auto now = TInstant::Now();
    if (now > event.ApproxDeliveryTime) {
        Metrics.Add(now - event.ApproxDeliveryTime);
    } else {
        Metrics.Add(TDuration::Zero());
    }
    --InFly;
}

void TSender::OnMetricsSchedule(TMetricsScheduleEvent& event) {
    Y_UNUSED(event);
    Metrics.InFly = InFly;
    Metrics.InFlySender = SenderId;
    Metrics.Count += 2;
    Send(MetricsAID, new TMetricsHolder::TMetricsEvent(Metrics));
    Metrics.Clear();

    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}

