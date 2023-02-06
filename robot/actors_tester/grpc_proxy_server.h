#pragma once

#include "metrics.h"

#include <robot/zora/tools/actors_tester/grpc/proto/proto.pb.h>

#include <robot/zora/algo/actors/base.h>
#include <robot/zora/tools/actors_tester/grpc/server.h>

using namespace NZora;

// gets TPing, hardcore waits WaitTime, sends back TPong
class TGrpcProxyServer : public TSimpleActor {
public:
    class TPingEvent;
    class TPongEvent;
    class TMetricsScheduleEvent : public TEvent<TMetricsScheduleEvent> {};

    TGrpcProxyServer(TActorId metricsAID, TDuration metricsDelay, TDuration waitTime);
    ~TGrpcProxyServer() = default;

    void OnAfterRegister() override;

    void OnPing(TPingEvent& event);
    void OnMetricsSchedule(TMetricsScheduleEvent& event);

private:
    TDuration WaitTime;

    TActorId MetricsAID;
    TDuration MetricsDelay;
    TMetrics Metrics;
};

class TGrpcProxyServer::TPingEvent : public TEvent<TGrpcProxyServer::TPingEvent> {
public:
    TPingEvent(TInstant approxDeliveryTime, const TActorId& sender, TString request)
        : ApproxDeliveryTime(approxDeliveryTime)
        , Sender(sender)
        , Request(request)
    {}

    TInstant ApproxDeliveryTime;
    TActorId Sender;
    TString Request;
};

class TGrpcProxyServer::TPongEvent : public TEvent<TGrpcProxyServer::TPongEvent> {
public:
    TPongEvent(TInstant approxDeliveryTime)
        : ApproxDeliveryTime(approxDeliveryTime)
    {}

    TInstant ApproxDeliveryTime;
};


// receive message from grpc, sends ping to proxy, awaits pong, sends back
class TGrpcSenderServer : public TSimpleActor {
public:
    class TSendEvent : public TEvent<TSendEvent> {};
    class TMetricsScheduleEvent : public TEvent<TMetricsScheduleEvent> {};

    TGrpcSenderServer(TString uri, TActorId metricsAID, TDuration metricsDelay, TActorId proxyAID);

    void OnAfterRegister() override;

    void OnPong(TGrpcProxyServer::TPongEvent& event);
//    void OnSend(TSendEvent& event);
    void OnMetricsSchedule(TMetricsScheduleEvent& event);
    void GotRequest(NAsyncGrpcTest::Request request);

private:
    TActorId Proxy;
    ui32 InFly;
    ui32 SenderId;

    TActorId MetricsAID;
    TDuration MetricsDelay;
    TMetrics Metrics;

    TGrpcServer Server;
};
