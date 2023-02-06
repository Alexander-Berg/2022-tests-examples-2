#pragma once

#include "metrics.h"

#include <robot/zora/algo/actors/base.h>

using namespace NZora;

class TRequest : public TSimpleActor {
public:
    class TPingEvent;
    class TKillEvent : public TEvent<TKillEvent> {};

    TRequest(TActorId metricsAID, TDuration pingDelay, TDuration killDelay);
    ~TRequest() = default;

    void OnAfterRegister() override;

    void OnPing(TPingEvent& event);
    void OnKill(TKillEvent& event);

private:
    TDuration PingDelay;
    TDuration KillDelay;

    TActorId MetricsAID;

    TMetrics Metrics;
};

class TRequest::TPingEvent : public TEvent<TRequest::TPingEvent> {
public:
    TPingEvent(TInstant approxDeliveryTime)
        : ApproxDeliveryTime(approxDeliveryTime)
    {}

    TInstant ApproxDeliveryTime;
};



class TRequestCreator : public TSimpleActor {
public:
    class TWakeUp : public TEvent<TWakeUp> {};

    TRequestCreator(ui32 rate, TActorId metricsAID, TDuration pingDelay, TDuration killDelay);
    ~TRequestCreator() = default;

    void OnAfterRegister() override;

    void OnWakeUp(TWakeUp& event);

private:
    ui32 Rate;

    TActorId MetricsAID;
    TDuration PingDelay;
    TDuration KillDelay;
};





