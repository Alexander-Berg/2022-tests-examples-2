#pragma once

#include "metrics.h"

#include <robot/zora/algo/actors/base.h>

using namespace NZora;

class TPinger : public TSimpleActor {
public:
    class TPingEvent;
    class TMetricsScheduleEvent;

    TPinger(TActorId metricsAID, TDuration metricsDelay, TDuration pingDelay);
    ~TPinger() = default;

    void SetDst(TVector<TActorId> dst) {
        std::swap(Dst, dst);
    }

    void OnAfterRegister() override;

    void OnPing(TPingEvent& event);
    void OnMetricsScheduler(TMetricsScheduleEvent& event);

private:
    TVector<TActorId> Dst;
    size_t DstIterator;
    TDuration PingDelay;

    TActorId MetricsAID;
    TDuration MetricsDelay;

    TMetrics Metrics;
};

class TPinger::TPingEvent : public TEvent<TPinger::TPingEvent> {
public:
    TPingEvent(TInstant approxDeliveryTime)
        : ApproxDeliveryTime(approxDeliveryTime)
    {}

    TInstant ApproxDeliveryTime;
};

class TPinger::TMetricsScheduleEvent : public TEvent<TPinger::TMetricsScheduleEvent> {};







