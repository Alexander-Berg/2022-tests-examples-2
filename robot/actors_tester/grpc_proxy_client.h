#pragma once

#include "metrics.h"

#include <robot/zora/algo/actors/base.h>
#include <robot/zora/tools/actors_tester/grpc/client.h>

using namespace NZora;

// gets TPing, send it via grpc to server, sends back TPong when receive answer
class TGrpcProxyClient : public TSimpleActor {
public:
    class TPingEvent;
    class TPongEvent;
    class TMetricsScheduleEvent : public TEvent<TMetricsScheduleEvent> {};

    TGrpcProxyClient(TActorId metricsAID, TDuration metricsDelay, TString uri);
    ~TGrpcProxyClient() = default;

    void OnAfterRegister() override;

    void OnPing(TPingEvent& event);
    void OnMetricsSchedule(TMetricsScheduleEvent& event);

private:
    TDuration WaitTime;

    TActorId MetricsAID;
    TDuration MetricsDelay;
    TMetrics Metrics;

    TGrpcClient GrpcClient;
};

class TGrpcProxyClient::TPingEvent : public TEvent<TGrpcProxyClient::TPingEvent> {
public:
    TPingEvent(TInstant approxDeliveryTime, const TActorId& sender)
        : ApproxDeliveryTime(approxDeliveryTime)
        , Sender(sender)
    {}

    TInstant ApproxDeliveryTime;
    TActorId Sender;
};

class TGrpcProxyClient::TPongEvent : public TEvent<TGrpcProxyClient::TPongEvent> {
public:
    TPongEvent(bool ok, TString& errorMsg, TInstant approxDeliveryTime)
        : Ok(ok)
          , ErrorMsg(errorMsg)
          , ApproxDeliveryTime(approxDeliveryTime)
    {}

    bool Ok;
    TString ErrorMsg;
    TInstant ApproxDeliveryTime;
};


// sends ping to proxy, awaits pong, counts unanswered events
class TGrpcSenderClient : public TSimpleActor {
public:
    class TSendEvent : public TEvent<TSendEvent> {};
    class TMetricsScheduleEvent : public TEvent<TMetricsScheduleEvent> {};

    TGrpcSenderClient(TActorId metricsAID, TDuration metricsDelay, TActorId proxyAID, ui32 rate);

    void OnAfterRegister() override;

    void OnPong(TGrpcProxyClient::TPongEvent& event);
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
