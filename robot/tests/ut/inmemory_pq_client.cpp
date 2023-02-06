#include "inmemory_pq_client.h"

#include <robot/rthub/misc/common.h>

#include <util/string/printf.h>

using namespace NPersQueue2;

namespace NRTHub {
    TString TInmemoryQueue::FormatPartitionName(ui32 partition) {
        return Sprintf("%s:%d", Name.c_str(), partition);
    }

    TInmemoryQueue& TInmemoryPQ::CreateQueue(const TString& name, size_t partitionsCount) {
        auto queue = MakeHolder<TInmemoryQueue>();
        queue->Name = name;
        queue->Partitions.resize(partitionsCount);
        Queues.push_back(std::move(queue));
        return *Queues.back();
    }

    TInmemoryQueue& TInmemoryPQ::GetQueue(const TString& name) const {
        auto it = FindIf(Queues, [&name](const THolder<TInmemoryQueue>& q) { return q->Name == name; });
        Y_VERIFY(it != Queues.end(), "queue [%s] not found", name.c_str());
        return **it;
    }

    TInmemoryConsumerSession::TInmemoryConsumerSession(TInmemoryQueuePartition& partition,
                                                       TAtomicSharedPtr<NPersQueue2::ICallBack>&& callback,
                                                       ui32 batchSize)
        : Partition(partition)
        , Callback(std::move(callback))
        , SoftOffset(NPersQueue2::NO_POSITION_CHANGE)
        , HardOffset(NPersQueue2::NO_POSITION_CHANGE)
        , Offset(-1)
        , BatchSize(batchSize)
    {
    }

    void TInmemoryConsumerSession::RunCycle() {
        TAtomicSharedPtr<TVector<TBuffer>> batch = MakeHolder<TVector<TBuffer>>();
        TVector<TOneProducerInfo> producerInfo;
        {
            bool softCommit = true;
            const TConsumerRecId offset = Callback->BeforeRead(&softCommit);
            SetOffset(offset, softCommit);
        }
        {
            for (size_t i = static_cast<size_t>(Offset + 1); i < Partition.Queue.size() && batch->size() < BatchSize; ++i) {
                TBuffer buffer;
                const TString& message = Partition.Queue[i];
                buffer.Append(message.data(), message.size());
                batch->push_back(std::move(buffer));
                TOneProducerInfo oneProducerInfo;
                oneProducerInfo.Offset = i;
                producerInfo.push_back(oneProducerInfo);
            }
        }
        {
            bool softCommit = true;
            const TConsumerRecId offset = Callback->AfterRead(0, &softCommit);
            SetOffset(offset, softCommit);
        }
        {
            const TConsumerRecId nextPos = producerInfo.size() > 0 ? producerInfo.back().Offset : Offset;
            bool softCommit = true;
            const TConsumerRecId offset = Callback->DoOnData(batch, producerInfo, nextPos, &softCommit);
            SetOffset(offset, softCommit);
        }
    }

    TInmemoryPQConsumer::TInmemoryPQConsumer(TInmemoryQueue& queue, THolder<NPersQueue2::ICallBack>&& callback,
                                             ui32 batchSize)
        : Queue(queue)
        , Started(false)
        , CallbackPrototype(std::move(callback))
        , BatchSize(batchSize)
    {
    }

    TInmemoryConsumerSession& TInmemoryPQConsumer::StartSession(ui32 partition) {
        auto newSession = MakeHolder<TInmemoryConsumerSession>(Queue.Partitions.at(partition),
                                                               CallbackPrototype->Clone(Queue.FormatPartitionName(partition), 0, 0, NewPromise()),
                                                               BatchSize);
        ActiveSessions.push_back(std::move(newSession));
        return *ActiveSessions.back();
    }

    void TInmemoryPQConsumer::StartBackgroundPolling() {
        PollStopped = NewPromise();
        PollThread.Reset(new std::thread([this]() {
            while (!PollStopped.GetFuture().Wait(TDuration::MilliSeconds(1))) {
                for (THolder<TInmemoryConsumerSession>& s : ActiveSessions) {
                    s->RunCycle();
                }
            }
        }));
    }

    void TInmemoryPQConsumer::StopBackgroundPolling() {
        if (PollStopped.Initialized()) {
            PollStopped.SetValue();
            PollThread->join();
            PollStopped = TPromise<void>();
        }
    }

    void TInmemoryConsumerSession::SetOffset(TConsumerRecId offset, bool softCommit) {
        if (offset == NO_POSITION_CHANGE) {
            return;
        }
        if (softCommit) {
            Y_VERIFY(offset >= HardOffset);
            SoftOffset = offset;
        } else {
            Y_VERIFY(offset >= HardOffset);
            HardOffset = offset;
            Partition.ReadOffset = static_cast<i32>(HardOffset);
        }
        Offset = static_cast<i32>(offset);
    }

    TInmemoryPQClient::TInmemoryPQClient(TInmemoryPQ& inmemoryPQ)
        : InmemoryPQ(inmemoryPQ)
        , ActiveConsumers()
    {
    }

    THolder<IPQConsumer> TInmemoryPQClient::CreateConsumer(const TConsumerParameters& parameters, THolder<ICallBack>&& callback) {
        auto result = MakeHolder<TInmemoryPQConsumer>(InmemoryPQ.GetQueue(FormatName(parameters.Settings)),
                                                      std::move(callback), parameters.BatchSize);
        //указатель в ActiveConsumers может протухнить при разрушении результирующего TInmemoryPQConsumer
        ActiveConsumers.push_back(result.Get());
        return std::move(result);
    }

    TMaybe<TPartitionsState> TInmemoryPQClient::PullOffsets(const TPQConfig& config, const TString&, bool) {
        THashMap<TString, TPartitionState> result;
        TInmemoryQueue& inmemoryQueue = InmemoryPQ.GetQueue(FormatName(config));
        for (size_t i = 0; i < inmemoryQueue.Partitions.size(); ++i) {
            const TInmemoryQueuePartition& partition = inmemoryQueue.Partitions[i];
            TPartitionState state{};
            state.LastWrittenOffset = static_cast<i64>(partition.Queue.size()) - 1;
            state.Lag = state.LastWrittenOffset > partition.ReadOffset
                            ? static_cast<ui64>(state.LastWrittenOffset - partition.ReadOffset - 1)
                            : 0;
            Y_VERIFY(result.emplace(inmemoryQueue.FormatPartitionName(i), std::move(state)).second);
        }
        return TPartitionsState(std::move(result));
    }
}
