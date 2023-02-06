#pragma once

#include "metrics.h"

#include <robot/zora/algo/actors/base.h>

using namespace NZora;

// gets TPing, hardcore waits WaitTime, sends back TPong
class TProxy : public TSimpleActor {
public:
    class TPingEvent;
    class TPongEvent;
    class TMetricsScheduleEvent : public TEvent<TMetricsScheduleEvent> {};

    TProxy(TActorId metricsAID, TDuration metricsDelay, TDuration waitTime);
    ~TProxy() = default;

    void OnAfterRegister() override;

    void OnPing(TPingEvent& event);
    void OnMetricsSchedule(TMetricsScheduleEvent& event);

private:
    TDuration WaitTime;

    TActorId MetricsAID;
    TDuration MetricsDelay;
    TMetrics Metrics;
};

class TProxy::TPingEvent : public TEvent<TProxy::TPingEvent> {
public:
    TPingEvent(TInstant approxDeliveryTime, const TActorId& sender)
        : ApproxDeliveryTime(approxDeliveryTime)
        , Sender(sender)
    {}

    TInstant ApproxDeliveryTime;
    TActorId Sender;
};

class TProxy::TPongEvent : public TEvent<TProxy::TPongEvent> {
public:
    TPongEvent(TInstant approxDeliveryTime)
        : ApproxDeliveryTime(approxDeliveryTime)
    {}

    TInstant ApproxDeliveryTime;
};


// sends ping to proxy, awaits pong, counts unanswered events
class TSender : public TSimpleActor {
public:
    class TSendEvent : public TEvent<TSendEvent> {};
    class TMetricsScheduleEvent : public TEvent<TMetricsScheduleEvent> {};

    TSender(TActorId metricsAID, TDuration metricsDelay, TActorId proxyAID, ui32 rate);

    void OnAfterRegister() override;

    void OnPong(TProxy::TPongEvent& event);
    void OnSend(TSendEvent& event);
    void OnMetricsSchedule(TMetricsScheduleEvent& event);

private:
    TActorId Proxy;
    ui32 Rate;
    ui32 InFly;
    ui32 SenderId;

    TActorId MetricsAID;
    TDuration MetricsDelay;
    TMetrics Metrics;
};
