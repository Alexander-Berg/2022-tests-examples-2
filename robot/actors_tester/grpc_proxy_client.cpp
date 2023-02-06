#include "grpc_proxy_client.h"

#include <robot/zora/algo/zlog/zlog.h>

TGrpcProxyClient::TGrpcProxyClient(TActorId metricsAID, TDuration metricsDelay, TString uri)
    : MetricsAID(metricsAID)
    , MetricsDelay(metricsDelay)
    , GrpcClient(uri)
{
    AddHandler(&TGrpcProxyClient::OnPing);
    AddHandler(&TGrpcProxyClient::OnMetricsSchedule);
    GrpcClient.Start();
}

void TGrpcProxyClient::OnAfterRegister() {
    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}

void TGrpcProxyClient::OnPing(TPingEvent& event) {
    auto now = TInstant::Now();
    if (now > event.ApproxDeliveryTime) {
        Metrics.Add(now - event.ApproxDeliveryTime);
    } else {
        Metrics.Add(TDuration::Zero());
    }

    TActorId sender = event.Sender;
    GrpcClient.GetResponse("ololo", [sender](bool ok, NAsyncGrpcTest::Response, TString errorMsg){
        NRobot::TActorSystem::Send(sender, MakeHolder<TPongEvent>(ok, errorMsg, TInstant::Now()));
    });
}

void TGrpcProxyClient::OnMetricsSchedule(TMetricsScheduleEvent& event) {
    Y_UNUSED(event);
    Metrics.Count += 2;
    Send(MetricsAID, new TMetricsHolder::TMetricsEvent(Metrics));
    Metrics.Clear();

    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}


static ui32 SenderIdGenerator = 0;

TGrpcSenderClient::TGrpcSenderClient(TActorId metricsAID, TDuration metricsDelay, TActorId proxyAID, ui32 rate)
    : Proxy(proxyAID)
    , Rate(rate)
    , InFly(0)
    , SenderId(++SenderIdGenerator)
    , MetricsAID(metricsAID)
    , MetricsDelay(metricsDelay)
{
    AddHandler(&TGrpcSenderClient::OnPong);
    AddHandler(&TGrpcSenderClient::OnSend);
    AddHandler(&TGrpcSenderClient::OnMetricsSchedule);
}

void TGrpcSenderClient::OnAfterRegister() {
    Schedule(MetricsDelay, new TMetricsScheduleEvent);
    Schedule(TDuration::Seconds(1), new TSendEvent);
}

void TGrpcSenderClient::OnSend(TSendEvent& event) {
    Y_UNUSED(event);
    InFly += Rate;
    auto now = TInstant::Now();
    for (size_t i = 0; i < Rate; ++i) {
        Send(Proxy, new TGrpcProxyClient::TPingEvent(now, SelfId()));
    }
    Schedule(TDuration::Seconds(1), new TSendEvent);
}

void TGrpcSenderClient::OnPong(TGrpcProxyClient::TPongEvent& event) {
    Y_UNUSED(event);
    auto now = TInstant::Now();
    if (now > event.ApproxDeliveryTime) {
        Metrics.Add(now - event.ApproxDeliveryTime);
    } else {
        Metrics.Add(TDuration::Zero());
    }
    if (event.ErrorMsg) {
        Cerr << event.ErrorMsg << Endl;
    }
    --InFly;
}

void TGrpcSenderClient::OnMetricsSchedule(TMetricsScheduleEvent& event) {
    Y_UNUSED(event);
    Metrics.InFly = InFly;
    Metrics.InFlySender = SenderId;
    Metrics.Count += 2;
    Send(MetricsAID, new TMetricsHolder::TMetricsEvent(Metrics));
    Metrics.Clear();

    Schedule(MetricsDelay, new TMetricsScheduleEvent);
}
