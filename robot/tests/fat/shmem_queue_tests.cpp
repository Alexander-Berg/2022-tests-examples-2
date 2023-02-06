#include <robot/rthub/misc/debug_logger.h>
#include <robot/rthub/misc/io.h>
#include <robot/rthub/misc/shmem_queue.h>
#include <robot/rthub/misc/system.h>
#include <robot/rthub/misc/signals.h>
#include <ydb/library/yql/utils/backtrace/backtrace.h>

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/protobuf/util/pb_io.h>

#include <util/digest/fnv.h>
#include <util/generic/guid.h>
#include <util/random/entropy.h>
#include <util/random/random.h>
#include <util/random/shuffle.h>
#include <util/string/split.h>
#include <util/system/event.h>
#include <util/system/mutex.h>
#include <util/system/getpid.h>

#include <thread>
#include <sys/wait.h>
#include <sys/syscall.h>

using namespace NRTHub;

//#define ENABLE_DBG_LOG

class TSharedMemoryQueueFatTest: public TTestBase {
private:
    UNIT_TEST_SUITE(TSharedMemoryQueueFatTest);

    UNIT_TEST(TestRobust);
    UNIT_TEST_SUITE_END();
private:
    struct TPendingRequest {
        TVector<char> Request;
        ui32 LastAttemptNumber{0};
        ui64 ResponsesCount{0};
        ui64 ResponsesHash{0};
    };

    enum class EOutputMessageType {
        Response = 1,
        Confirmation = 2
    };

    struct TOutputMessageHeader {
        EOutputMessageType Type;
        ui32 InputMessageId;
        union {
            struct {
                bool Completed;
                ui32 ResponsesCount;
                ui64 ResponsesHash;
                ui32 LastAttemptNumber;
            };
            struct {
                ui32 AttemptNumber;
            };
        };
    };

public:
    static ui32 ReadUi32(const char*& bytes, size_t& size) {
        ui32 result;
        Y_VERIFY(size >= sizeof(result));
        memcpy(&result, bytes, sizeof(result));
        bytes += sizeof(result);
        size -= sizeof(result);
        return result;
    }

    static const TOutputMessageHeader* ReadHeader(const TTransaction& tran, const char*& bytes, size_t& size) {
        bytes = tran.GetBytes();
        size = tran.GetSize();
        const auto* result = tran.As<TOutputMessageHeader>();
        bytes += sizeof(TOutputMessageHeader);
        size -= sizeof(TOutputMessageHeader);
        return result;
    }

    static ui64 ReadBlockFnv(size_t blockSize, const char*& bytes, size_t& size) {
        const auto result = FnvHash<ui64>(bytes, blockSize);
        bytes += blockSize;
        size -= blockSize;
        return result;
    }

    static int ReadAndCompare(const TVector<char>& expected, const char*& bytes, size_t& size) {
        Y_VERIFY(size >= expected.size());
        const auto result = memcmp(expected.data(), bytes, expected.size());
        bytes += expected.size();
        size -= expected.size();
        return result;
    }

#ifdef ENABLE_DBG_LOG
    static void StartLogger() {
        TDebugLogger::Get().Start();
    }

    static void StopLogger() {
        TDebugLogger::Get().Stop();
    }

    static void Log(const TString& messsage) {
        TDebugLogger::Get().Write(messsage);
    }

    //response: R:char|input_message_id:ui32|data
    //confirmation: C:char|input_message_id:ui32|completed:char=C,0|responses_count:ui32|request
    static void LogOutputTran(pid_t pid, const char* message, const TTransaction& tran) {
        TStringBuilder logBuilder;

        const char* bytes;
        size_t size;
        const auto* outputHeader = ReadHeader(tran, bytes, size);
        if (outputHeader->Type == EOutputMessageType::Confirmation) {
            logBuilder << Sprintf("[%d] %s (%u, %u, %u, %u, %lu, %u)|(%lu, %lu)",
                                  pid,
                                  message,
                                  static_cast<ui32>(outputHeader->Type),
                                  outputHeader->InputMessageId,
                                  static_cast<ui32>(outputHeader->Completed),
                                  outputHeader->ResponsesCount,
                                  outputHeader->ResponsesHash,
                                  outputHeader->LastAttemptNumber,
                                  size,
                                  ReadBlockFnv(size, bytes, size));
        } else {
            logBuilder << Sprintf("[%d] %s (%u, %u, %u)|(%lu, %lu)",
                                  pid,
                                  message,
                                  static_cast<ui32>(outputHeader->Type),
                                  outputHeader->InputMessageId,
                                  outputHeader->AttemptNumber,
                                  size,
                                  ReadBlockFnv(size, bytes, size));
        }
        logBuilder << "\n";
        Log(logBuilder);
    }

    static void LogInputTran(pid_t pid, const char* message, const TTransaction& tran) {
        TStringBuilder logBuilder;

        const char* bytes = tran.GetBytes();
        size_t size = tran.GetSize();
        logBuilder << Sprintf("[%d] %s ", pid, message);
        if (TStringBuf(bytes, size) == "__stop__") {
            logBuilder << "stop";
        } else {
            const ui32 messageId = ReadUi32(bytes, size);
            logBuilder << Sprintf("(%u, %lu, %lu)",
                                  messageId,
                                  size,
                                  ReadBlockFnv(size, bytes, size));
        }
        logBuilder << "\n";
        Log(logBuilder);
    }
#else
    inline static void StartLogger() {
    }

    inline static void StopLogger() {
    }

    inline static void Log(const TString&) {
    }

    inline static void LogOutputTran(pid_t, const char*, const TTransaction&) {
    }

    inline static void LogInputTran(pid_t, const char*, const TTransaction&) {
    }
#endif

    static constexpr size_t TestItemsCount = 1000000;
    static constexpr size_t MaxMessageSize = 1000;
    static constexpr size_t MaxResponsesCount = 20;
    static constexpr size_t MaxResponseSize = 200;
    static constexpr size_t MaxKillDelayMillis = 10;
    static constexpr size_t MaxVictimsCount = 3;
    static constexpr size_t SlavesCount = 10;

    void TestRobust() {
        auto inputQueue = MakeSharedMemoryQueue(100);
        auto outputQueue = MakeSharedMemoryQueue(100);
        TNotificationHandle stopSpawner;

        Log(Sprintf("main test started [%d]\n", GetPID()));
        const pid_t spawnerPid = DoFork();
        if (spawnerPid == 0) {
            RunSpawner(*inputQueue, *outputQueue, stopSpawner);
        }
        StartLogger();
        outputQueue->MakeReadonly();

        TMutex lock;
        THashMap<ui32, TPendingRequest> pendingRequests;
        std::thread receiver([&]() { ReceiveResponses(*outputQueue, pendingRequests, lock); });

        std::atomic<bool> stopSpawnerWatcher(false);
        std::thread spawnerWatcher([&]() {
            while (!stopSpawnerWatcher.load()) {
                CheckAlive(spawnerPid);
                Sleep(TDuration::MilliSeconds(100));
            }
        });

        Cout << "START TIME: [" << TInstant::Now() << "]" << Endl;
        SendRequests(*inputQueue, pendingRequests, lock);
        outputQueue->Stop();
        receiver.join();
        Cout << "FINISH TIME: [" << TInstant::Now() << "]" << Endl;

        stopSpawnerWatcher.store(true);
        spawnerWatcher.join();

        {
            stopSpawner.Raise();
            int status;
            UNIT_ASSERT(DoWaitPid(spawnerPid, &status, 0) == spawnerPid);
            UNIT_ASSERT(!WIFSIGNALED(status));
            UNIT_ASSERT(WIFEXITED(status));
            UNIT_ASSERT_VALUES_EQUAL(WEXITSTATUS(status), 0);
        }

        const auto inputQueueStats = inputQueue->GetStats();
        const auto outputQueueStats = outputQueue->GetStats();

        inputQueue.Destroy();
        Log("input queue destroyed\n");
        outputQueue.Destroy();
        Log("output queue destroyed\n");
        StopLogger();

        Cout << Sprintf("input queue (%lu, %lu), output queue (%lu, %lu)",
                        inputQueueStats.OwnerDeathCount, inputQueueStats.RetriedOperationsCount,
                        outputQueueStats.OwnerDeathCount, outputQueueStats.RetriedOperationsCount)
             << Endl;
        UNIT_ASSERT(inputQueueStats.OwnerDeathCount + outputQueueStats.OwnerDeathCount > 0);
        UNIT_ASSERT(inputQueueStats.RetriedOperationsCount + outputQueueStats.RetriedOperationsCount > 0);
    }

private:
    void SendRequests(ISharedMemoryQueue& inputQueue,
                      THashMap<ui32, TPendingRequest>& pendingRequests,
                      TMutex& lock)
    {
        for (ui32 i = 0; i < TestItemsCount; ++i) {
            auto message = GenerateRandomBytes(MaxMessageSize);
            TEnqueueScope scope(inputQueue, sizeof(i) + message.size());
            UNIT_ASSERT(scope.Transaction.Defined());
            char* bytes = scope.Transaction->GetBytes();

            memcpy(bytes, &i, sizeof(i));
            bytes += sizeof(i);

            memcpy(bytes, message.data(), message.size());

            with_lock(lock) {
                Y_VERIFY(pendingRequests.insert({i, TPendingRequest{std::move(message)}}).second);
            }
        }
        while (true) {
            with_lock(lock) {
                if (pendingRequests.empty()) {
                    break;
                }
            }
            Sleep(TDuration::MilliSeconds(1));
        }
    }

    void ReceiveResponses(ISharedMemoryQueue& outputQueue,
                          THashMap<ui32, TPendingRequest>& pendingRequests,
                          TMutex& lock)
    {
        Log(Sprintf("receiver started [%d, %lu]\n", GetPID(), DoGetTid()));
        while (true) {
            TDequeueScope scope(outputQueue);
            if (!scope.Transaction.Defined()) {
                break;
            }
            const char* bytes;
            size_t size;
            const auto* header = ReadHeader(*scope.Transaction, bytes, size);
            LogOutputTran(999, "receiver", *scope.Transaction);

            auto& pendingRequest = [&]() -> TPendingRequest& {
                with_lock(lock) {
                    auto it = pendingRequests.find(header->InputMessageId);
                    UNIT_ASSERT(it != pendingRequests.end());
                    return it->second;
                }
            }();

            //response: R:char|input_message_id:ui32|data
            //confirmation: C:char|input_message_id:ui32|completed:char=C,0|responses_count:ui32|request
            if (header->Type == EOutputMessageType::Confirmation) {
                UNIT_ASSERT_VALUES_EQUAL(header->Completed, true);
                UNIT_ASSERT_VALUES_EQUAL(header->ResponsesCount, pendingRequest.ResponsesCount);
                UNIT_ASSERT_VALUES_EQUAL(header->ResponsesHash, pendingRequest.ResponsesHash);
                UNIT_ASSERT_VALUES_EQUAL(header->LastAttemptNumber, pendingRequest.LastAttemptNumber);
                UNIT_ASSERT_VALUES_EQUAL(ReadAndCompare(pendingRequest.Request, bytes, size), 0);
                with_lock(lock) {
                    UNIT_ASSERT(pendingRequests.erase(header->InputMessageId) == 1);
                }
            } else {
                if (header->AttemptNumber != pendingRequest.LastAttemptNumber) {
                    pendingRequest.LastAttemptNumber = header->AttemptNumber;
                    pendingRequest.ResponsesCount = 0;
                    pendingRequest.ResponsesHash = 0;
                }
                ++pendingRequest.ResponsesCount;
                pendingRequest.ResponsesHash = CombineHashes(pendingRequest.ResponsesHash,
                                                             FnvHash<ui64>(bytes, bytes + size));
            }
        }
    }

    void RunSpawner(ISharedMemoryQueue& inputQueue, ISharedMemoryQueue& outputQueue, TNotificationHandle& stop) {
        const auto spawnerStartInstant = TInstant::Now();
        Log(Sprintf("spawner started [%d]\n", GetPID()));
        inputQueue.DiscardOwnership();
        outputQueue.DiscardOwnership();
        TVector<pid_t> slavePids(SlavesCount);
        bool doKill = true;

        bool isFirst = true;
        while (!stop.Wait()) {
            if (doKill) {
                doKill = TInstant::Now() - spawnerStartInstant < TDuration::Seconds(40);
                if (!doKill) {
                    Log(Sprintf("[%d] killer stopped\n", GetPID()));
                }
            }

            if (isFirst) {
                isFirst = false;
            } else  {
                for (auto pid: slavePids) {
                    CheckAlive(pid);
                }
                if (doKill) {
                    TVector<pid_t*> victimPids(slavePids.size());
                    for (size_t i = 0; i < victimPids.size(); ++i) {
                        victimPids[i] = &slavePids[i];
                    }
                    Shuffle(victimPids.begin(), victimPids.end());
                    const auto victimsCount = RandomNumber<size_t>(MaxVictimsCount + 1);
                    for (size_t i = 0; i < victimsCount; ++i) {
                        const auto victimPid = *victimPids[i];
                        Log(Sprintf("before kill [%d]\n", victimPid));
                        DoKill(victimPid, SIGKILL);
                        int status;
                        UNIT_ASSERT_VALUES_EQUAL(DoWaitPid(victimPid, &status, 0), victimPid);
                        UNIT_ASSERT(WIFSIGNALED(status));
                        UNIT_ASSERT_VALUES_EQUAL(WTERMSIG(status), SIGKILL);
                        Log(Sprintf("after kill [%d]\n", victimPid));
                    }
                    for (size_t i = 0; i < victimsCount; ++i) {
                        auto& deadPid = *victimPids[i];
                        inputQueue.Repair(deadPid);
                        outputQueue.Repair(deadPid);
                        deadPid = 0;
                    }
                }
            }
            for (ui8 clientId = 0; clientId < SlavesCount; ++clientId) {
                if (slavePids[clientId] != 0) {
                    continue;
                }
                const pid_t slavePid = DoFork();
                if (slavePid == 0) {
                    RunSlave(inputQueue, outputQueue, clientId);
                }
                slavePids[clientId] = slavePid;
            }
            Sleep(TDuration::MilliSeconds(RandomNumber<ui32>(MaxKillDelayMillis + 1)));
        }
        for (size_t i = 0; i < slavePids.size(); ++i) {
            Enqueue(inputQueue, "__stop__");
        }
        for (pid_t pid: slavePids) {
            int status;
            UNIT_ASSERT(DoWaitPid(pid, &status, 0) == pid);
            UNIT_ASSERT(!WIFSIGNALED(status));
            UNIT_ASSERT(WIFEXITED(status));
            UNIT_ASSERT_VALUES_EQUAL(WEXITSTATUS(status), 0);
        }
        Log(Sprintf("[%d] spawner normal exit\n", GetPID()));
        exit(0);
    }

    void RunSlave(ISharedMemoryQueue& inputQueue, ISharedMemoryQueue& outputQueue, ui8 clientId) {
        const auto pid = GetPID();
        Log(Sprintf("slave started [%lu, %d, %lu]\n", static_cast<ui64>(clientId), pid, DoGetTid()));
        inputQueue.MakeReadonly();
        inputQueue.SetClientId(clientId + 1);
        outputQueue.SetClientId(clientId + 1);

        TMaybe<TTransaction> inputTran;
        TMaybe<TTransaction> confirmationTran;
        TOutputMessageHeader* confirmationHeader = nullptr;
        {
            auto inputTrans = inputQueue.GetPendingTransactions();
            auto outputTrans = outputQueue.GetPendingTransactions();

            Log(Sprintf("[%d] pending input trans [%lu], pending output trans [%lu]\n",
                        pid, inputTrans.size(), outputTrans.size()));

            for (auto& outputTran: outputTrans) {
                const auto* h = outputTran.As<TOutputMessageHeader>();
                if (h->Type == EOutputMessageType::Confirmation) {
                    Y_VERIFY(!confirmationTran.Defined());
                    Log(Sprintf("[%d] confirmation found, completed [%u]\n",
                                pid, static_cast<ui32>(h->Completed)));
                    confirmationTran = std::move(outputTran);
                    confirmationHeader = confirmationTran->As<TOutputMessageHeader>();
                }
            }

            if (!inputTrans.empty()) {
                UNIT_ASSERT_VALUES_EQUAL(inputTrans.size(), 1);
                auto& t = inputTrans[0];
                const auto* bytes = t.GetBytes();
                size_t size = t.GetSize();
                if (confirmationHeader && confirmationHeader->Completed) {
                    UNIT_ASSERT_VALUES_EQUAL(ReadUi32(bytes, size), confirmationHeader->InputMessageId);
                    LogInputTran(pid, "pending input committing", inputTrans[0]);
                    inputQueue.Commit(t);
                    Log(Sprintf("[%d] committed\n", pid));
                } else {
                    inputTran = std::move(t);
                    Log(Sprintf("[%d] input tran set for processing\n", pid));
                }
            }
            for (auto& outputTran: outputTrans) {
                LogOutputTran(pid, "pending output", outputTran);
                const auto* h = outputTran.As<TOutputMessageHeader>();
                if (h->Type == EOutputMessageType::Confirmation) {
                    Y_VERIFY(h == confirmationHeader);
                    if (h->Completed) {
                        outputQueue.Commit(outputTran);
                        confirmationTran = Nothing();
                        confirmationHeader = nullptr;
                        Log(Sprintf("[%d] committed\n", pid));
                    } else {
                        Log(Sprintf("[%d] non completed confirmation set for processing\n", pid));
                    }
                } else {
                    outputQueue.Rollback(outputTran);
                    Log(Sprintf("[%d] rolled back\n", pid));
                }
            }
            Log(Sprintf("[%d] process pending trans finished\n", pid));
        }
        while (true) {
            if (!inputTran) {
                inputTran = inputQueue.Dequeue();
            }
            Y_VERIFY(inputTran.Defined());
            LogInputTran(pid, "slave received tran", *inputTran);
            if (inputTran->AsStringBuf() == "__stop__") {
                inputQueue.Commit(*inputTran);
                break;
            }

            const char* inputBytes = inputTran->GetBytes();
            size_t inputSize = inputTran->GetSize();

            ui32 inputMessageId = ReadUi32(inputBytes, inputSize);

            //response: R:char|input_message_id:ui32|data
            //confirmation: C:char|input_message_id:ui32|completed:char=C,0|responses_count:ui32|request
            {
                if (!confirmationTran) {
                    confirmationTran = outputQueue.Enqueue(sizeof(TOutputMessageHeader) + inputSize,
                                                           TAllocOptions::For<TOutputMessageHeader>());
                    Y_VERIFY(confirmationTran.Defined());
                    auto* outputBytes = confirmationTran->GetBytes() + sizeof(TOutputMessageHeader);
                    memcpy(outputBytes, inputBytes, inputSize);
                    confirmationHeader = confirmationTran->As<TOutputMessageHeader>();
                    confirmationHeader->InputMessageId = inputMessageId;
                    confirmationHeader->Type = EOutputMessageType::Confirmation;
                }
                UNIT_ASSERT_VALUES_EQUAL(confirmationHeader->Completed, false);
                confirmationHeader->ResponsesCount = 0;
                confirmationHeader->ResponsesHash = 0;
                ++confirmationHeader->LastAttemptNumber;
            }

            const auto responsesCount = RandomNumber<ui64>(MaxResponsesCount) + 1;
            for (size_t i = 0; i < responsesCount; ++i) {
                const auto response = GenerateRandomBytes(MaxResponseSize);
                auto tran = outputQueue.Enqueue(sizeof(TOutputMessageHeader) + response.size(),
                                                TAllocOptions::For<TOutputMessageHeader>());
                UNIT_ASSERT(tran.Defined());
                auto* h = tran->As<TOutputMessageHeader>();
                h->Type = EOutputMessageType::Response;
                h->InputMessageId = inputMessageId;
                h->AttemptNumber = confirmationHeader->LastAttemptNumber;
                auto* outputBytes = tran->GetBytes() + sizeof(TOutputMessageHeader);
                memcpy(outputBytes, response.data(), response.size());

                LogOutputTran(pid, "response committing", *tran);
                outputQueue.Commit(*tran);
                Log(Sprintf("[%d] committed\n", pid));

                ++confirmationHeader->ResponsesCount;
                confirmationHeader->ResponsesHash = CombineHashes(confirmationHeader->ResponsesHash,
                                                                  FnvHash<ui64>(response));
            }

            LogOutputTran(pid, "confirmation before complete", *confirmationTran);
            confirmationHeader->Completed = true;
            Log(Sprintf("[%d] confirmation marked as completed\n", pid));

            inputQueue.Commit(*inputTran);
            Log(Sprintf("[%d] input committed\n", pid));

            inputTran = Nothing();
            outputQueue.Commit(*confirmationTran);
            Log(Sprintf("[%d] confirmation committed\n", pid));
            confirmationTran = Nothing();
            confirmationHeader = nullptr;

            UNIT_ASSERT_VALUES_EQUAL(inputQueue.GetPendingTransactions().size(), 0);
            UNIT_ASSERT_VALUES_EQUAL(outputQueue.GetPendingTransactions().size(), 0);
        }
        Log(Sprintf("[%d] slave normal exit\n", GetPID()));
        exit(0);
    }

    TVector<char> GenerateRandomBytes(size_t maxSize) {
        const auto size = RandomNumber<ui64>(maxSize) + 1;
        TVector<char> result(size);
        Y_VERIFY(EntropyPool().Load(result.data(), size) == size);
        return result;
    }

    void Enqueue(ISharedMemoryQueue& queue, const TString& s) {
        Enqueue(queue, s.data(), s.size());
    }

    void Enqueue(ISharedMemoryQueue& queue, const void* data, size_t size) {
        TEnqueueScope scope(queue, size);
        memcpy(scope.Transaction->GetBytes(), data, size);
    }

    static void CheckAlive(pid_t pid) {
        int status;
        const pid_t waitPidResult = DoWaitPid(pid, &status, WNOHANG);
        if (waitPidResult == 0) {
            return;
        }
        Y_VERIFY(waitPidResult == pid, "unexpected waitpid result");
        if (WIFSIGNALED(status)) {
            Y_FAIL("process [%d] dead by signal [%d]", pid, WTERMSIG(status));
        } else if (WIFEXITED(status)) {
            Y_FAIL("process [%d] exited with status [%d]", pid, WEXITSTATUS(status));
        } else {
            Y_FAIL("invalid waitpid result");
        }
    }
};

UNIT_TEST_SUITE_REGISTRATION(TSharedMemoryQueueFatTest);
