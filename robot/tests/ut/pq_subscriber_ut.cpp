#include "inmemory_pq_client.h"
#include "mocks.h"

#include <robot/rthub/impl/subscribers/pq_subscriber.h>

#include <library/cpp/testing/unittest/registar.h>
#include <robot/rthub/misc/common.h>
#include <thread>

using namespace NRTHub;
using namespace NPersQueue2;
using namespace NThreading;

class TPQSubscriberTest final: public TTestBase {
private:
    UNIT_TEST_SUITE(TPQSubscriberTest);
    UNIT_TEST(TestSimple);
    UNIT_TEST(TestSkipOffsetsForPartitionsWithBiggestLagOnly);
    UNIT_TEST_SUITE_END();

    THolder<TConfig> Config;
    TInputConfig* InputConfig;
    TIntrusivePtr<TRTHubCounters> RTHubCounters;
    TIntrusivePtr<TAggRTHubCounters> AggRTHubCounters;
    THolder<TInmemoryPQ> InmemoryPQ;
    THolder<TInmemoryPQClient> PQClient;
    TIntrusivePtr<ISubscriber> Subscriber;
    TMockChannelExecutor* ChannelExecutor;

    TSubscriberTopicCounters& Counters() {
        return RTHubCounters->Subscribers.GetOrCreateByName(FormatName(InputConfig->GetSource()));
    }

    void Subscribe() {
        Subscriber = MakePQSubscriber(*Config, *PQClient, RTHubCounters, AggRTHubCounters, "", 0, 1, nullptr);
        THolder<TMockChannelExecutor> mockChannelExecutor = MakeHolder<TMockChannelExecutor>();
        ChannelExecutor = mockChannelExecutor.Get();
        Subscriber->Subscribe(*InputConfig, std::move(mockChannelExecutor));
        Subscriber->Start();
    }

    void WaitForReadOffset(TInmemoryConsumerSession& session, TConsumerRecId recId, TDuration timeout) {
        const TInstant timeoutAt = TInstant::Now() + timeout;
        while (true) {
            Y_VERIFY(TInstant::Now() < timeoutAt, "wait for BeforeRead offset timed out");
            bool softCommit = true;
            const TConsumerRecId offset = session.Callback->BeforeRead(&softCommit);
            if (offset >= recId) {
                return;
            }
        }
    }

public:
    void SetUp() override {
        Config = MakeHolder<TConfig>();
        TChannelConfig* channelConfig = Config->MutableChannel()->Add();
        InputConfig = channelConfig->MutableInput()->Add();
        InputConfig->MutableSource()->SetServer("bs-prod.logbroker.yandex.net");
        InputConfig->MutableSource()->SetIdent("zora");
        InputConfig->MutableSource()->SetLogType("pages-fresh");
        InputConfig->MutableSource()->SetClient("rthub-fresh");
        channelConfig->MutableYql()->SetPath("WebPages");
        channelConfig->MutableYql()->SetInputProto("NKwYT.TDocument");
        channelConfig->MutableYql()->SetOutputProto("NKwYT.TWebPagesItem");
        TChannelOutputConfig* outputConfig = channelConfig->MutableOutput()->Add();
        TPQConfig* queueConfig = outputConfig->MutableQueue()->Add();
        queueConfig->SetServer("bs-prod.logbroker.yandex.net");
        queueConfig->SetIdent("rthub-fresh");
        queueConfig->SetLogType("mercury");

        Config->MutableLimits()->SetCommitOffsetsPeriodSeconds(0);

        RTHubCounters = MakeIntrusive<TRTHubCounters>();
        AggRTHubCounters = MakeIntrusive<TAggRTHubCounters>();
        InmemoryPQ = MakeHolder<TInmemoryPQ>();
        PQClient = MakeHolder<TInmemoryPQClient>(*InmemoryPQ);
    }

    void TearDown() override {
        if (Subscriber) {
            if (ChannelExecutor) {
                ChannelExecutor->CompleteAll();
            }
            for (TInmemoryPQConsumer* c : PQClient->ActiveConsumers) {
                c->StartBackgroundPolling();
            }
            Subscriber->Stop();
            Subscriber.Reset();
        }
    }

    void TestSimple() {
        InputConfig->MutableSource()->SetBatchSize(1);

        TInmemoryQueue& inmemoryQueue = InmemoryPQ->CreateQueue(FormatName(InputConfig->GetSource()), 1);
        inmemoryQueue.Partitions[0].Append({"test-input-message"});

        UNIT_ASSERT_VALUES_EQUAL(0, PQClient->ActiveConsumers.size());
        Subscribe();
        UNIT_ASSERT_VALUES_EQUAL(1, PQClient->ActiveConsumers.size());
        TInmemoryPQConsumer* consumer = PQClient->ActiveConsumers[0];
        UNIT_ASSERT_VALUES_EQUAL(true, consumer->Started);

        TInmemoryConsumerSession& session = consumer->StartSession(0);
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().CallbacksCreated);

        session.RunCycle();
        UNIT_ASSERT_VALUES_EQUAL(NO_POSITION_CHANGE, session.SoftOffset);
        UNIT_ASSERT_VALUES_EQUAL(NO_POSITION_CHANGE, session.HardOffset);
        UNIT_ASSERT_VALUES_EQUAL(1, ChannelExecutor->SubmittedMessages.size());
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().InputMessagesCount);
        UNIT_ASSERT_VALUES_EQUAL(0, Counters().OutputMessagesCount);
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().InflightInputMessagesCount);
        UNIT_ASSERT_VALUES_EQUAL(0, Counters().InflightOutputMessagesCount);
        TMockChannelExecutor::TSubmittedMessage& submittedMessage = ChannelExecutor->SubmittedMessages[0];
        UNIT_ASSERT_VALUES_EQUAL(1, submittedMessage.IncomingMessage.Batch->size());
        UNIT_ASSERT_VALUES_EQUAL(0, submittedMessage.IncomingMessage.BatchIndex);
        UNIT_ASSERT_VALUES_EQUAL("test-input-message", submittedMessage.AsString());

        TVector<TIoOperation> ioOperations;
        TPromise<void> ioPromise;
        {
            ioPromise = NewPromise();
            ioOperations.push_back({ioPromise.GetFuture(), 42});
            submittedMessage.Promise.SetValue(std::move(ioOperations));
            ChannelExecutor->SubmittedMessages.pop_back();
        }
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().OutputMessagesCount);
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().InflightOutputMessagesCount);
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().InflightInputMessagesCount);

        ioPromise.SetValue();
        UNIT_ASSERT_VALUES_EQUAL(0, Counters().InflightOutputMessagesCount);
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().InflightInputMessagesCount);

        session.RunCycle();
        UNIT_ASSERT_VALUES_EQUAL(0, session.SoftOffset);
        UNIT_ASSERT_VALUES_EQUAL(0, session.HardOffset);
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().InputMessagesCount);
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().OutputMessagesCount);
        UNIT_ASSERT_VALUES_EQUAL(0, Counters().InflightInputMessagesCount);
    }

    void TestSkipOffsetsForPartitionsWithBiggestLagOnly() {
        InputConfig->MutableSource()->SetBatchSize(3);
        Config->MutableChannel()->Mutable(0)->MutableInput(0)->SetSkipByAbsoluteLag(2);
        Config->SetSkipOffsetsUpdatePeriodMillis(10);

        TInmemoryQueue& inmemoryQueue = InmemoryPQ->CreateQueue(FormatName(InputConfig->GetSource()), 3);
        inmemoryQueue.Partitions[0].Append({"m1"});
        inmemoryQueue.Partitions[1].Append({"m2", "m3"});
        inmemoryQueue.Partitions[2].Append({"m4", "m5", "m6"});

        Subscribe();

        TInmemoryPQConsumer* consumer = PQClient->ActiveConsumers.at(0);
        TInmemoryConsumerSession& session0 = consumer->StartSession(0);
        TInmemoryConsumerSession& session1 = consumer->StartSession(1);
        TInmemoryConsumerSession& session2 = consumer->StartSession(2);

        WaitForReadOffset(session2, 0, TDuration::Seconds(1));
        UNIT_ASSERT_VALUES_EQUAL(1, Counters().SkippedCount);

        session0.RunCycle();
        ChannelExecutor->CompleteAll({"m1"});

        session1.RunCycle();
        ChannelExecutor->CompleteAll({"m2", "m3"});

        session2.RunCycle();
        ChannelExecutor->CompleteAll({"m5", "m6"});
    }
};

UNIT_TEST_SUITE_REGISTRATION(TPQSubscriberTest);
