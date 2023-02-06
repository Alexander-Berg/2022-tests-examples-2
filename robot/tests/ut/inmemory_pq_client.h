#pragma once

#include <robot/rthub/impl/pq/pq_client.h>

#include <thread>

namespace NRTHub {
    struct TInmemoryQueuePartition {
        TVector<TString> Queue;
        i32 ReadOffset{-1};

        void Append(TVector<TString> messages) {
            Queue.insert(end(Queue), begin(messages), end(messages));
        }
    };

    struct TInmemoryQueue {
        TString Name;
        TVector<TInmemoryQueuePartition> Partitions;

        TString FormatPartitionName(ui32 partition);
    };

    class TInmemoryPQ {
    public:
        TInmemoryQueue& CreateQueue(const TString& name, size_t partitionsCount);

        TInmemoryQueue& GetQueue(const TString& name) const;

        TVector<THolder<TInmemoryQueue>> Queues;
    };

    struct TInmemoryConsumerSession {
        TInmemoryConsumerSession(TInmemoryQueuePartition& partition,
                                 TAtomicSharedPtr<NPersQueue2::ICallBack>&& callback,
                                 ui32 batchSize);

        void RunCycle();

        void SetOffset(NPersQueue2::TConsumerRecId offset, bool softCommit);

        TInmemoryQueuePartition& Partition;
        TAtomicSharedPtr<NPersQueue2::ICallBack> Callback;
        NPersQueue2::TConsumerRecId SoftOffset;
        NPersQueue2::TConsumerRecId HardOffset;
        i32 Offset;
        ui32 BatchSize;
    };

    struct TInmemoryPQConsumer final: public IPQConsumer {
        TInmemoryPQConsumer(TInmemoryQueue& queue, THolder<NPersQueue2::ICallBack>&& callback, ui32 batchSize);

        void Start() override {
            Started = true;
        }

        virtual void Stop() override {
            StopBackgroundPolling();
            Started = false;
        }

        TInmemoryConsumerSession& StartSession(ui32 partition);

        void StartBackgroundPolling();

        void StopBackgroundPolling();

        TInmemoryQueue& Queue;
        bool Started;
        THolder<NPersQueue2::ICallBack> CallbackPrototype;
        ui32 BatchSize;
        TVector<THolder<TInmemoryConsumerSession>> ActiveSessions;
        THolder<std::thread> PollThread;
        TPromise<void> PollStopped;
    };

    class TInmemoryPQClient final: public IPQClient {
    public:
        explicit TInmemoryPQClient(TInmemoryPQ& inmemoryPQ);

        THolder<IPQConsumer> CreateConsumer(const TConsumerParameters& parameters, THolder<NPersQueue2::ICallBack>&& callback) override;

        THolder<NPersQueue::IConsumer> CreateNewProtocolConsumer(const NPersQueue::TConsumerSettings&) override {
            Y_FAIL("not implemented");
        }

        NThreading::TFuture<TCreateProducerResult> CreateProducer(const NPersQueue::TProducerSettings&) override {
            Y_FAIL("not implemented");
        }

        TMaybe<TPartitionsState> PullOffsets(const TPQConfig&, const TString&, bool) override;

        TInmemoryPQ& InmemoryPQ;
        TVector<TInmemoryPQConsumer*> ActiveConsumers;
    };
}
