#include "grpc_proxy_server.h"

#include <robot/zora/algo/zlog/zlog.h>

TGrpcProxyServer::TGrpcProxyServer(TActorId metricsAID, TDuration metricsDelay, TDuration waitTime)
    : WaitTime(waitTime)
    , MetricsAID(metricsAID)
    , MetricsDelay(metricsDelay)
{
    AddHandler(&TGrpcProxyServer::OnPing);
    AddHandler(&TGrpcProxyServer::OnMetricsSchedule);
}

void TGrpcProxyServer::OnAfterRegister() {
    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}

void TGrpcProxyServer::OnPing(TPingEvent& event) {
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

void TGrpcProxyServer::OnMetricsSchedule(TMetricsScheduleEvent& event) {
    Y_UNUSED(event);
    Metrics.Count += 2;
    Send(MetricsAID, new TMetricsHolder::TMetricsEvent(Metrics));
    Metrics.Clear();

    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}


static ui32 SenderIdGenerator = 0;

TGrpcSenderServer::TGrpcSenderServer(TString uri, TActorId metricsAID, TDuration metricsDelay, TActorId proxyAID)
    : Proxy(proxyAID)
    , InFly(0)
    , SenderId(++SenderIdGenerator)
    , MetricsAID(metricsAID)
    , MetricsDelay(metricsDelay)
    , Server(uri)
{
    AddHandler(&TGrpcSenderServer::OnPong);
    AddHandler(&TGrpcSenderServer::OnMetricsSchedule);
    Server.SetCallback([this](NAsyncGrpcTest::Request request){
        GotRequest(request);
    });
    Server.Start();
}

void TGrpcSenderServer::OnAfterRegister() {
    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}

//void TGrpcSenderServer::OnSend(TSendEvent& event) {
//    Y_UNUSED(event);
//    InFly++;
//    auto now = TInstant::Now();
//    Send(Proxy, new TGrpcProxyServer::TPingEvent(now, SelfId()));
//}

void TGrpcSenderServer::OnPong(TGrpcProxyServer::TPongEvent& event) {
    Y_UNUSED(event);
    auto now = TInstant::Now();
    if (now > event.ApproxDeliveryTime) {
        Metrics.Add(now - event.ApproxDeliveryTime);
    } else {
        Metrics.Add(TDuration::Zero());
    }
    --InFly;

    //Here we should send data to client
}

void TGrpcSenderServer::OnMetricsSchedule(TMetricsScheduleEvent& event) {
    Y_UNUSED(event);
    Metrics.InFly = InFly;
    Metrics.InFlySender = SenderId;
    Metrics.Count += 2;
    Send(MetricsAID, new TMetricsHolder::TMetricsEvent(Metrics));
    Metrics.Clear();

    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}

void TGrpcSenderServer::GotRequest(NAsyncGrpcTest::Request request)
{
    auto now = TInstant::Now();
    NZora::TActorSystem::Send(Proxy, MakeHolder<TGrpcProxyServer::TPingEvent>(now, SelfId(), request.GetSomeData()));
}

