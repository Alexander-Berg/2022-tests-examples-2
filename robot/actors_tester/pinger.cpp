#include "activities.h"
#include "pinger.h"
#include "metrics.h"

#include <robot/zora/algo/zlog/zlog.h>

TPinger::TPinger(TActorId metricsAID, TDuration metricsDelay, TDuration pingDelay)
    : DstIterator(0)
    , PingDelay(pingDelay)
    , MetricsAID(metricsAID)
    , MetricsDelay(metricsDelay)
{
    SetActivityType(AT_PINGER);
    AddHandler(&TPinger::OnPing);
    AddHandler(&TPinger::OnMetricsScheduler);
}

void TPinger::OnAfterRegister() {
    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}

void TPinger::OnPing(TPingEvent& event) {
    auto now = TInstant::Now();
    if (now > event.ApproxDeliveryTime) {
        Metrics.Add(now - event.ApproxDeliveryTime);
    } else {
        Metrics.Add(TDuration::Zero());
    }

    auto next = Dst[DstIterator];
    DstIterator = (DstIterator + 1) % Dst.size();

    if (MetricsDelay != TDuration::Zero()) {
        auto deliveryTime = now + PingDelay;
        TActorSystem::Schedule(deliveryTime, next, MakeHolder<TPingEvent>(deliveryTime));
    } else {
        Send(next, MakeHolder<TPingEvent>(now));
    }
}

void TPinger::OnMetricsScheduler(TMetricsScheduleEvent& event) {
    Y_UNUSED(event);
    Metrics.Count += 2;
    Send(MetricsAID, new TMetricsHolder::TMetricsEvent(Metrics));
    Metrics.Clear();

    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}

