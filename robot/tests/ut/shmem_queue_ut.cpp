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
#include <util/string/split.h>
#include <util/system/event.h>
#include <util/system/mutex.h>

#include <thread>

using namespace NRTHub;

class TSharedMemoryQueueTest: public TTestBase {
private:
    UNIT_TEST_SUITE(TSharedMemoryQueueTest);
    UNIT_TEST(TestSimple);
    UNIT_TEST(TestConcurrentReaders);
    UNIT_TEST(TestReadonly);
    UNIT_TEST(TestRemap);
    UNIT_TEST(TestManyPages);
    UNIT_TEST(TestStopReader);
    UNIT_TEST(TestCleanupDanglingPages);
    UNIT_TEST(TestOpenByName);
    UNIT_TEST(TestRollback);
    UNIT_TEST(TestZeroMemory);
    UNIT_TEST(TestAlignMemory);
    UNIT_TEST_SUITE_END();

public:
    void TestSimple() {
        constexpr size_t messagesCount = 10000;
        auto queue = MakeSharedMemoryQueue(10);
        const pid_t childPid = DoFork();
        if (childPid == 0) {
            queue->DiscardOwnership();
            queue->MakeReadonly();
            {
                for (size_t i = 0; i < messagesCount; ++i) {
                    TDequeueScope scope(*queue);
                    Y_VERIFY(scope.Transaction);
                    UNIT_ASSERT_VALUES_EQUAL(scope.Transaction->AsStringBuf(), Sprintf("test-message-%lu", i));
                }
                TDequeueScope scope(*queue);
                Y_VERIFY(scope.Transaction);
                UNIT_ASSERT_VALUES_EQUAL(scope.Transaction->AsStringBuf(), "stop");
            }

            exit(0);
        }

        std::atomic<bool> publisherDone(false);
        std::thread publisher([&]() {
            try {
                for (size_t i = 0; i < messagesCount; ++i) {
                    Enqueue(*queue, Sprintf("test-message-%lu", i));
                }
                publisherDone = true;
            }
            catch (...) {
                publisherDone = true;
                throw;
            }
        });

        const TInstant timeout = TInstant::Now() + TDuration::Seconds(5);
        while (true) {
            UNIT_ASSERT(TInstant::Now() < timeout);
            if (publisherDone.load()) {
                break;
            }
            int status;
            UNIT_ASSERT(DoWaitPid(childPid, &status, WNOHANG) == 0);
            Sleep(TDuration::MilliSeconds(5));
        }
        publisher.join();
        Enqueue(*queue, "stop");
        int status;
        UNIT_ASSERT(DoWaitPid(childPid, &status, 0) == childPid);
        UNIT_ASSERT(WIFEXITED(status));
        UNIT_ASSERT(WEXITSTATUS(status) == 0);
    }

    void TestConcurrentReaders() {
        constexpr size_t testMessagesCount = 100000;
        auto queue = MakeSharedMemoryQueue(100);
        ui64 sentMessagesHash = 0;
        std::atomic<ui64> receivedMessagesHash(0);
        std::atomic<ui64> receivedMessagesCount(0);
        TManualEvent allReceived;

        constexpr size_t readersCount = 5;
        TVector<TPipe> pipes(readersCount);
        TVector<pid_t> pids(readersCount);
        TVector<std::thread> receivers(readersCount);

        for (size_t i = 0; i < readersCount; ++i) {
            const pid_t childId = DoFork();
            TPipe& pipe = pipes[i];
            if (childId == 0) {
                try {
                    queue->DiscardOwnership();
                    queue->MakeReadonly();
                    pipe.Read.Close();
                    while (true) {
                        TDequeueScope scope(*queue);
                        Y_VERIFY(scope.Transaction);
                        if (scope.Transaction->AsStringBuf() == "stop-reading") {
                            break;
                        }
                        const char* bytes = scope.Transaction->GetBytes();
                        const ui64 hash = FnvHash<ui64>(bytes, scope.Transaction->GetSize());
                        UNIT_ASSERT(DoWrite(pipe.Write.Unwrap(), &hash, sizeof(hash)) == sizeof(hash));
                    }
                }
                catch(...)
                {
                    Cerr << "reader failed:\n" << CurrentExceptionMessage() << Endl;
                    throw;
                }
                exit(0);
            }
            pids[i] = childId;
            pipe.Write.Close();
            receivers[i] = std::thread([&] {
                try {
                    while (true) {
                        ui64 hash;
                        ssize_t readBytes = DoRead(pipe.Read.Unwrap(), &hash, sizeof(hash));
                        if (readBytes == 0) {
                            break;
                        }
                        UNIT_ASSERT(readBytes == sizeof(hash));
                        receivedMessagesHash += hash;
                        ++receivedMessagesCount;
                        if (receivedMessagesCount == testMessagesCount) {
                            allReceived.Signal();
                            break;
                        }
                    }
                }
                catch(...) {
                    Cerr << "receiver failed:\n" << CurrentExceptionMessage() << Endl;
                    throw;
                }
            });
        }
        for (size_t i = 0; i < testMessagesCount; ++i) {
            const size_t size = RandomNumber<ui64>(1000) + 500;
            auto message = GenerateRandomBytes(size);
            sentMessagesHash += FnvHash<ui64>(message);
            Enqueue(*queue, message.data(), message.size());
        }
        allReceived.Wait();
        for (size_t i = 0; i < readersCount; ++i) {
            char stopMessage[] = "stop-reading";
            Enqueue(*queue, stopMessage, sizeof(stopMessage) - 1);
        }
        for (pid_t childPid : pids) {
            int status;
            UNIT_ASSERT(DoWaitPid(childPid, &status, 0) == childPid);
            UNIT_ASSERT(WIFEXITED(status));
            UNIT_ASSERT(WEXITSTATUS(status) == 0);
        }
        for (auto& t : receivers) {
            t.join();
        }

        UNIT_ASSERT_VALUES_EQUAL(receivedMessagesCount.load(), testMessagesCount);
        UNIT_ASSERT_VALUES_EQUAL(receivedMessagesHash.load(), sentMessagesHash);

        UNIT_ASSERT(queue->GetStats().AllocatedPages >= 1);
    }

    void TestReadonly() {
        TPipe pipe;
        auto queue = MakeSharedMemoryQueue(10);
        const pid_t childPid = DoFork();

        constexpr char childMessage[] = "before-write";

        if (childPid == 0) {
            pipe.Read.Close();
            queue->DiscardOwnership();
            queue->MakeReadonly();

            TDequeueScope scope(*queue);
            Y_VERIFY(scope.Transaction);
            char* ptr = scope.Transaction->GetBytes();

            DoWrite(pipe.Write.Unwrap(), childMessage, sizeof(childMessage));
            ptr[1] = 42;

            Y_FAIL("unreachable");
        }
        pipe.Write.Close();
        Enqueue(*queue, "test-message");

        int status;
        const pid_t waitPidResult = DoWaitPid(childPid, &status, 0);
        Y_VERIFY(waitPidResult == childPid);

        char readMessage[sizeof(childMessage)];
        UNIT_ASSERT_VALUES_EQUAL(DoRead(pipe.Read.Unwrap(), readMessage, sizeof(readMessage)), sizeof(readMessage));
        UNIT_ASSERT_VALUES_EQUAL(TStringBuf(childMessage), TStringBuf(readMessage));

        UNIT_ASSERT(WIFSIGNALED(status));
        UNIT_ASSERT_VALUES_EQUAL(SIGSEGV, WTERMSIG(status));
    }

    void TestRemap() {
        TPipe pipe;
        auto queue = MakeSharedMemoryQueue(1);
        constexpr size_t pageSize = 4 * 1024 * 1024;

        const pid_t childPid = DoFork();
        if (childPid == 0) {
            pipe.Read.Close();
            queue->DiscardOwnership();
            queue->MakeReadonly();
            {
                Sleep(TDuration::MilliSeconds(50));
                for (size_t i = 0; i < 3; ++i) {
                    TDequeueScope scope(*queue);
                    Y_VERIFY(scope.Transaction);
                    DoWrite(pipe.Write.Unwrap(), scope.Transaction->GetBytes(), scope.Transaction->GetSize());
                }
                pipe.Write.Close();
                TDequeueScope scope(*queue);
                Y_VERIFY(scope.Transaction);
                UNIT_ASSERT_VALUES_EQUAL(scope.Transaction->AsStringBuf(), "stop");
            }
            exit(0);
        }
        pipe.Write.Close();

        std::atomic<bool> readerDone(false);
        TVector<char> readData;
        std::thread reader([&]() {
            try {
                constexpr size_t bufferSize = 1024;
                char buffer[bufferSize];
                ssize_t readCount;
                while((readCount = DoRead(pipe.Read.Unwrap(), buffer, bufferSize)) > 0) {
                    readData.insert(readData.end(), buffer, buffer + readCount);
                }
                readerDone = true;
            } catch(...) {
                readerDone = true;
                throw;
            }
        });

        TVector<char> expectedOutput;
        EnqueueRandomMessage(*queue, pageSize, expectedOutput);
        EnqueueRandomMessage(*queue, pageSize * 3, expectedOutput);
        EnqueueRandomMessage(*queue, pageSize * 3, expectedOutput);

        const TInstant timeout = TInstant::Now() + TDuration::Seconds(5);
        while (true) {
            UNIT_ASSERT(TInstant::Now() < timeout);
            if (readerDone.load()) {
                break;
            }
            int status;
            UNIT_ASSERT(DoWaitPid(childPid, &status, WNOHANG) == 0);
            Sleep(TDuration::MilliSeconds(5));
        }

        reader.join();
        Enqueue(*queue, "stop");
        int status;
        UNIT_ASSERT(DoWaitPid(childPid, &status, 0) == childPid);
        UNIT_ASSERT(WIFEXITED(status));
        UNIT_ASSERT(WEXITSTATUS(status) == 0);

        UNIT_ASSERT(expectedOutput == readData);
    }

    void TestManyPages() {
        TPipe pipe;
        auto queue = MakeSharedMemoryQueue(3);

        constexpr size_t pageSize = 4 * 1024 * 1024;
        TVector<char> expectedOutput;
        EnqueueRandomMessage(*queue, pageSize, expectedOutput);
        EnqueueRandomMessage(*queue, pageSize, expectedOutput);
        EnqueueRandomMessage(*queue, pageSize, expectedOutput);

        {
            TSharedMemoryQueueStats stats = queue->GetStats();
            UNIT_ASSERT_VALUES_EQUAL(3, stats.ItemsInQueueCount);
            UNIT_ASSERT_VALUES_EQUAL(3, stats.AllocatedPages);
            UNIT_ASSERT_VALUES_EQUAL(3 * pageSize, stats.AllocatedBytes);
            UNIT_ASSERT_VALUES_EQUAL(3, stats.UsedPages);
            UNIT_ASSERT_VALUES_EQUAL(3 * pageSize, stats.UsedBytes);
        }

        const pid_t childPid = DoFork();
        if (childPid == 0) {
            pipe.Read.Close();
            queue->DiscardOwnership();
            queue->MakeReadonly();
            {
                for (size_t i = 0; i < 4; ++i) {
                    TDequeueScope scope(*queue);
                    Y_VERIFY(scope.Transaction);
                    DoWrite(pipe.Write.Unwrap(), scope.Transaction->GetBytes(), scope.Transaction->GetSize());
                }
                pipe.Write.Close();
                TDequeueScope scope(*queue);
                Y_VERIFY(scope.Transaction);
                UNIT_ASSERT_VALUES_EQUAL(scope.Transaction->AsStringBuf(), "stop");
            }
            exit(0);
        }
        pipe.Write.Close();

        std::atomic<bool> readerDone(false);
        TVector<char> readData;
        std::thread reader([&]() {
            try {
                constexpr size_t bufferSize = 1024;
                char buffer[bufferSize];
                ssize_t readCount;
                while((readCount = DoRead(pipe.Read.Unwrap(), buffer, bufferSize)) > 0) {
                    readData.insert(readData.end(), buffer, buffer + readCount);
                }
                readerDone = true;
            } catch(...) {
                readerDone = true;
                throw;
            }
        });

        const size_t bigMessageSize = RandomNumber<ui64>() % 30 * 1024 * 1024 + 10 * 1024 * 1024;
        EnqueueRandomMessage(*queue, bigMessageSize, expectedOutput);

        const TInstant timeout = TInstant::Now() + TDuration::Seconds(5);
        while (true) {
            UNIT_ASSERT(TInstant::Now() < timeout);
            if (readerDone.load()) {
                break;
            }
            int status;
            UNIT_ASSERT(DoWaitPid(childPid, &status, WNOHANG) == 0);
            Sleep(TDuration::MilliSeconds(5));
        }

        reader.join();
        Enqueue(*queue, "stop");
        int status;
        UNIT_ASSERT(DoWaitPid(childPid, &status, 0) == childPid);
        UNIT_ASSERT(WIFEXITED(status));
        UNIT_ASSERT(WEXITSTATUS(status) == 0);

        UNIT_ASSERT(expectedOutput == readData);

        {
            TSharedMemoryQueueStats stats = queue->GetStats();
            UNIT_ASSERT_VALUES_EQUAL(0, stats.ItemsInQueueCount);
            UNIT_ASSERT_VALUES_EQUAL(3, stats.AllocatedPages);
            UNIT_ASSERT_VALUES_EQUAL(2 * pageSize + bigMessageSize, stats.AllocatedBytes);
            UNIT_ASSERT_VALUES_EQUAL(0, stats.UsedPages);
            UNIT_ASSERT_VALUES_EQUAL(0, stats.UsedBytes);
        }
    }

    void TestStopReader() {
        auto queue = MakeSharedMemoryQueue(3);
        std::atomic<bool> beforeDequeue(false);
        std::atomic<bool> afterDequeue(false);
        auto readerThread = std::thread([&] {
            beforeDequeue = true;
            TDequeueScope scope(*queue);
            UNIT_ASSERT(!scope.Transaction);
            afterDequeue = true;
        });
        Sleep(TDuration::MilliSeconds(500));
        UNIT_ASSERT(beforeDequeue.load());
        UNIT_ASSERT(!afterDequeue.load());
        queue->Stop();
        readerThread.join();
        UNIT_ASSERT(beforeDequeue.load());
        UNIT_ASSERT(afterDequeue.load());
    }

    void TestCleanupDanglingPages() {
        auto queue = MakeSharedMemoryQueue(3);
        Enqueue(*queue, "test-message");

        {
            const pid_t childPid = DoFork();
            if (childPid == 0) {
                queue->DiscardOwnership();
                queue->MakeReadonly();
                queue->SetClientId(1);
                auto dequeueTransaction = queue->Dequeue();
                UNIT_ASSERT(dequeueTransaction);
                UNIT_ASSERT_VALUES_EQUAL(dequeueTransaction->AsStringBuf(), "test-message");
                exit(42);
            }
            int status;
            UNIT_ASSERT(DoWaitPid(childPid, &status, 0) == childPid);
            UNIT_ASSERT(WIFEXITED(status));
            UNIT_ASSERT(WEXITSTATUS(status) == 42);

            auto stats = queue->GetStats();
            UNIT_ASSERT_VALUES_EQUAL(stats.InflightItemsCount, 1);
            UNIT_ASSERT_VALUES_EQUAL(stats.AllocatedPages, 1);
            UNIT_ASSERT_VALUES_EQUAL(stats.UsedPages, 1);
            UNIT_ASSERT_VALUES_EQUAL(stats.PendingEnqueueTransactionsCount, 0);
            UNIT_ASSERT_VALUES_EQUAL(stats.PendingDequeueTransactionsCount, 1);
        }

        {
            UNIT_ASSERT(queue->GetPendingTransactions().empty());

            const pid_t childPid = DoFork();
            if (childPid == 0) {
                queue->DiscardOwnership();
                queue->MakeReadonly();
                queue->SetClientId(1);

                UNIT_ASSERT_VALUES_EQUAL(queue->GetPendingTransactions().size(), 1);
                auto tran = std::move(queue->GetPendingTransactions()[0]);
                UNIT_ASSERT_VALUES_EQUAL(tran.AsStringBuf(), "test-message");
                queue->Commit(tran);
                UNIT_ASSERT(queue->GetPendingTransactions().empty());

                exit(43);
            }
            int status;
            UNIT_ASSERT(DoWaitPid(childPid, &status, 0) == childPid);
            UNIT_ASSERT(WIFEXITED(status));
            UNIT_ASSERT(WEXITSTATUS(status) == 43);

            auto stats = queue->GetStats();
            UNIT_ASSERT_VALUES_EQUAL(stats.InflightItemsCount, 0);
            UNIT_ASSERT_VALUES_EQUAL(stats.AllocatedPages, 1);
            UNIT_ASSERT_VALUES_EQUAL(stats.UsedPages, 0);
            UNIT_ASSERT_VALUES_EQUAL(stats.PendingEnqueueTransactionsCount, 0);
            UNIT_ASSERT_VALUES_EQUAL(stats.PendingDequeueTransactionsCount, 0);
        }
    }

    void TestOpenByName() {
        TNotificationHandle serverReady(false);
        const auto queueName = Sprintf("shmem-queue-test-%s", CreateGuidAsString().c_str());
        static constexpr auto testItemsCount = 1000;

        const auto clientPid = DoFork();
        if (clientPid == 0) {
            serverReady.Wait();
            {
                auto sharedMemoryQueue = OpenSharedMemoryQueue(queueName);
                for (size_t i = 0; i < testItemsCount; ++i) {
                    const auto data = Sprintf("test-data-%lu\n", i);
                    TEnqueueScope enqueueScope(*sharedMemoryQueue, data.size());
                    data.copy(enqueueScope.Transaction->GetBytes(), data.size());
                }
            }
            exit(0);
        }

        TPipe serverPipe;
        const auto serverPid = DoFork();
        if (serverPid == 0) {
            serverPipe.Read.Close();
            {
                auto sharedMemoryQueue = MakeSharedMemoryQueue(100, queueName);
                serverReady.Raise();
                for (size_t i = 0; i < testItemsCount; ++i) {
                    TDequeueScope dequeueScope(*sharedMemoryQueue);
                    DoWrite(serverPipe.Write.Unwrap(),
                            dequeueScope.Transaction->GetBytes(), dequeueScope.Transaction->GetSize());
                }
            }
            exit(0);
        }
        serverPipe.Write.Close();

        TString receivedData;
        while (true) {
            char buffer[100];
            ssize_t readBytes = DoRead(serverPipe.Read.Unwrap(), buffer, sizeof(buffer));
            if (readBytes == 0) {
                break;
            }
            receivedData.append(buffer, static_cast<size_t>(readBytes));
        }
        TVector<TString> items;
        StringSplitter(receivedData).SplitByString(TString("\n")).SkipEmpty().AddTo(&items);
        UNIT_ASSERT_VALUES_EQUAL(items.size(), testItemsCount);
        for (size_t i = 0; i < testItemsCount; ++i) {
            const auto expected = Sprintf("test-data-%lu", i);
            UNIT_ASSERT_VALUES_EQUAL(items[i], expected);
        }

        int status;
        Y_VERIFY(DoWaitPid(clientPid, &status, 0) == clientPid);
        Y_VERIFY(DoWaitPid(serverPid, &status, 0) == serverPid);
    }

    void TestRollback() {
        constexpr size_t testItemsCount = 100000;
        constexpr size_t slavesCount = 10;
        constexpr size_t maxMessageSize = 1000;
        constexpr size_t rollbacksFrequency = 13;

        auto inputQueue = MakeSharedMemoryQueue(100);
        auto outputQueue = MakeSharedMemoryQueue(100);
        TVector<pid_t> slavePids(slavesCount);
        TMutex lock;
        TVector<TVector<char>> unmatchedItems;

        for (ui8 i = 0; i < slavePids.size(); ++i) {
            const pid_t slavePid = DoFork();
            if (slavePid == 0) {
                inputQueue->SetClientId(i + 1);
                inputQueue->DiscardOwnership();
                inputQueue->MakeReadonly();
                outputQueue->DiscardOwnership();
                outputQueue->SetClientId(i + 1);

                ui32 nextEnqueueRollback = RandomNumber<ui32>(rollbacksFrequency);
                ui32 nextDequeueRollback = RandomNumber<ui32>(rollbacksFrequency);
                while (true) {
                    auto inputTran = inputQueue->Dequeue();
                    UNIT_ASSERT(inputTran.Defined());
                    if (inputTran->AsStringBuf() == "__stop__") {
                        inputQueue->Commit(*inputTran);
                        break;
                    }
                    if (nextDequeueRollback == 0) {
                        inputQueue->Rollback(*inputTran);
                        nextDequeueRollback = RandomNumber<ui32>(rollbacksFrequency);
                        continue;
                    }
                    --nextDequeueRollback;
                    TVector<char> message(inputTran->GetBytes(), inputTran->GetBytes() + inputTran->GetSize());
                    Reverse(message.begin(), message.end());
                    auto outputTran = outputQueue->Enqueue(message.size());
                    Copy(message.begin(), message.end(), outputTran->GetBytes());
                    if (nextEnqueueRollback == 0) {
                        outputQueue->Rollback(*outputTran);
                        inputQueue->Rollback(*inputTran);
                        nextEnqueueRollback = RandomNumber<ui32>(rollbacksFrequency);
                        continue;
                    }
                    --nextEnqueueRollback;
                    outputQueue->Commit(*outputTran);
                    inputQueue->Commit(*inputTran);
                }
                exit(0);
            }
            slavePids[i] = slavePid;
        }

        outputQueue->MakeReadonly();

        std::thread receiver([&]() {
            for (size_t i = 0; i < testItemsCount; ++i) {
                TVector<char> message;
                {
                    TDequeueScope scope(*outputQueue);
                    UNIT_ASSERT(scope.Transaction.Defined());
                    message = TVector<char>(scope.Transaction->GetBytes(),
                                            scope.Transaction->GetBytes() + scope.Transaction->GetSize());
                }
                Reverse(message.begin(), message.end());
                with_lock(lock) {
                    auto it = Find(unmatchedItems, message);
                    UNIT_ASSERT(it != unmatchedItems.end());
                    if (it != std::prev(unmatchedItems.end())) {
                        *it = std::move(unmatchedItems.back());
                    }
                    unmatchedItems.pop_back();
                }
            }
        });

        for (size_t i = 0; i < testItemsCount; ++i) {
            auto message = GenerateRandomBytes(RandomNumber<ui64>(maxMessageSize) + 1);
            auto tran = inputQueue->Enqueue(message.size());
            UNIT_ASSERT(tran.Defined());
            Copy(message.begin(), message.end(), tran->GetBytes());
            with_lock(lock) {
                unmatchedItems.push_back(std::move(message));
            }
            inputQueue->Commit(*tran);
        }

        receiver.join();
        for (size_t i = 0; i < slavePids.size(); ++i) {
            Enqueue(*inputQueue, "__stop__");
        }
        for (pid_t pid: slavePids) {
            int status;
            UNIT_ASSERT(DoWaitPid(pid, &status, 0) == pid);
            UNIT_ASSERT(!WIFSIGNALED(status));
            UNIT_ASSERT(WIFEXITED(status));
            UNIT_ASSERT_VALUES_EQUAL(WEXITSTATUS(status), 0);
        }

        UNIT_ASSERT_VALUES_EQUAL(unmatchedItems.size(), 0);
    }

    void TestZeroMemory() {
        auto queue = MakeSharedMemoryQueue(1);
        {
            auto tran = queue->Enqueue(1, TAllocOptions{1, 1});
            UNIT_ASSERT(tran.Defined());
            UNIT_ASSERT_VALUES_EQUAL(tran->GetBytes()[0], 0);
            tran->GetBytes()[0] = 42;
            queue->Commit(*tran);
        }

        {
            auto tran = queue->Dequeue();
            UNIT_ASSERT(tran.Defined());
            queue->Commit(*tran);
        }

        {
            auto tran = queue->Enqueue(1, TAllocOptions{1, 1});
            UNIT_ASSERT(tran.Defined());
            UNIT_ASSERT_VALUES_EQUAL(tran->GetBytes()[0], 0);
            queue->Rollback(*tran);
        }
    }

    void TestAlignMemory() {
        auto queue = MakeSharedMemoryQueue(2);
        {
            auto t1 = queue->Enqueue(10, TAllocOptions{8, 0});
            auto t2 = queue->Enqueue(10, TAllocOptions{8, 0});
            UNIT_ASSERT((reinterpret_cast<ui64>(t1->GetBytes()) & 7) == 0);
            UNIT_ASSERT((reinterpret_cast<ui64>(t2->GetBytes()) & 7) == 0);
        }
    }

    TVector<char> GenerateRandomBytes(size_t size) {
        TVector<char> result(size);
        Y_VERIFY(EntropyPool().Load(result.data(), size) == size);
        return result;
    }

private:
    void Enqueue(ISharedMemoryQueue& queue, const TString& s) {
        Enqueue(queue, s.data(), s.size());
    }

    void Enqueue(ISharedMemoryQueue& queue, const void* data, size_t size) {
        TEnqueueScope scope(queue, size);
        memcpy(scope.Transaction->GetBytes(), data, size);
    }

    void EnqueueRandomMessage(ISharedMemoryQueue& queue, size_t size, TVector<char>& sentBytes) {
        const auto message = GenerateRandomBytes(size);
        Enqueue(queue, message.data(), message.size());
        sentBytes.insert(sentBytes.end(), message.begin(), message.end());
    }
};

UNIT_TEST_SUITE_REGISTRATION(TSharedMemoryQueueTest);
