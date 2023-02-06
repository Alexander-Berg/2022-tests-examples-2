#include <robot/rthub/misc/io.h>
#include <robot/rthub/misc/semirobust_mutex.h>
#include <robot/rthub/misc/system.h>
#include <util/system/getpid.h>

#include <library/cpp/testing/unittest/registar.h>

#include <sys/mman.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>

using namespace NRTHub;

struct TSharedData {
    TSemiRobustMutex Mutex;
    size_t Counter;
    std::atomic<size_t> Sync;
    std::atomic<size_t> Sync2;
};

class TSemiRobustMutexTest: public TTestBase {
private:
    UNIT_TEST_SUITE(TSemiRobustMutexTest);
    UNIT_TEST(TestSimple);
    UNIT_TEST(TestWakeUpSomeWaiterIfCurrentLockHolderDies);
    UNIT_TEST(TestDieMultipleTimes);
    UNIT_TEST(TestConcurrentCounter);
    UNIT_TEST(TestKillInUnlock);
    UNIT_TEST_SUITE_END();

public:
    void TearDown() override {
        if (SharedData) {
            DestroySharedData(SharedData);
            SharedData = nullptr;
        }
    }

    void TestSimple() {
        TNotificationHandle readyToDie(false);
        SharedData = CreateSharedData();
        const pid_t slavePid = DoFork();
        if (slavePid == 0) {
            ResetThreadContext();
            AcquireSemiRobustMutex(SharedData->Mutex);
            readyToDie.Raise();
            Sleep(TDuration::Hours(1));
            _Exit(0);
        }
        readyToDie.Wait();
        CheckAlive(slavePid);
        DoKill(slavePid, SIGKILL);
        WaitSignaled(slavePid, SIGKILL);

        UNIT_ASSERT_VALUES_EQUAL(GetSemiRobustMutexOwnerPid(SharedData->Mutex), slavePid);
        ReleaseSemiRobustMutex(SharedData->Mutex);
        AcquireSemiRobustMutex(SharedData->Mutex);
        ReleaseSemiRobustMutex(SharedData->Mutex);
    }

    void TestWakeUpSomeWaiterIfCurrentLockHolderDies() {
        TNotificationHandle readyToDie(false);
        SharedData = CreateSharedData();
        const pid_t slave1Pid = DoFork();
        if (slave1Pid == 0) {
            ResetThreadContext();
            AcquireSemiRobustMutex(SharedData->Mutex);
            readyToDie.Raise();
            Sleep(TDuration::Hours(1));
            _Exit(0);
        }
        readyToDie.Wait();
        const pid_t slave2Pid = DoFork();
        if (slave2Pid == 0) {
            ResetThreadContext();
            AcquireSemiRobustMutex(SharedData->Mutex);
            ++SharedData->Counter;
            ReleaseSemiRobustMutex(SharedData->Mutex);
            _Exit(0);
        }
        Sleep(TDuration::MilliSeconds(50));
        DoKill(slave1Pid, SIGKILL);
        WaitSignaled(slave1Pid, SIGKILL);
        UNIT_ASSERT_VALUES_EQUAL(GetSemiRobustMutexOwnerPid(SharedData->Mutex), slave1Pid);
        ReleaseSemiRobustMutex(SharedData->Mutex);
        WaitNormalExit(slave2Pid);

        UNIT_ASSERT_VALUES_EQUAL(SharedData->Counter, 1);
        AcquireSemiRobustMutex(SharedData->Mutex);
        ReleaseSemiRobustMutex(SharedData->Mutex);
    }

    void TestDieMultipleTimes() {
        constexpr size_t processesCount = 20;

        TNotificationHandle readyToDie(false);
        SharedData = CreateSharedData();
        const pid_t slavePid = DoFork();
        if (slavePid == 0) {
            ResetThreadContext();
            AcquireSemiRobustMutex(SharedData->Mutex);
            readyToDie.Raise();
            Sleep(TDuration::Hours(1));
            _Exit(0);
        }
        readyToDie.Wait();
        TVector<pid_t> pids(processesCount);
        for (auto& pid: pids) {
            pid = DoFork();
            if (pid == 0) {
                ResetThreadContext();
                AcquireSemiRobustMutex(SharedData->Mutex);
                ++SharedData->Counter;
                _Exit(0);
            }
        }
        Sleep(TDuration::MilliSeconds(50));
        DoKill(slavePid, SIGKILL);
        WaitSignaled(slavePid, SIGKILL);
        UNIT_ASSERT_VALUES_EQUAL(GetSemiRobustMutexOwnerPid(SharedData->Mutex), slavePid);
        ReleaseSemiRobustMutex(SharedData->Mutex);
        while (!pids.empty()) {
            size_t deadPid = WaitAnyProcessNormalExit(pids);
            UNIT_ASSERT_VALUES_EQUAL(GetSemiRobustMutexOwnerPid(SharedData->Mutex), deadPid);
            ReleaseSemiRobustMutex(SharedData->Mutex);
        }
        UNIT_ASSERT_VALUES_EQUAL(SharedData->Counter, processesCount);
        UNIT_ASSERT_VALUES_EQUAL(GetSemiRobustMutexOwnerPid(SharedData->Mutex), 0);

        AcquireSemiRobustMutex(SharedData->Mutex);
        ReleaseSemiRobustMutex(SharedData->Mutex);
    }

//TSemiRobustLock
//  took [68]
//  took [76]
//  took [76]
//  took [77]
//glibc
//  took [129]
//  took [127]
//musl
//  took [560]
//  took [586]
//  took [528]
//  took [694]
    void TestConcurrentCounter() {
        constexpr size_t processesCount = 10;
        constexpr size_t eachProcessCountTo = 100000;

        SharedData = CreateSharedData();
        TVector<pid_t> pids(processesCount);
        for (auto& pid: pids) {
            pid = DoFork();
            if (pid == 0) {
                ResetThreadContext();
                DoFutexWait(*(int*)(&SharedData->Sync), 0);
                for (size_t i = 0; i < eachProcessCountTo; ++i) {
                    AcquireSemiRobustMutex(SharedData->Mutex);
                    ++SharedData->Counter;
                    ReleaseSemiRobustMutex(SharedData->Mutex);
                }
                _Exit(0);
            }
        }
        const auto start = TInstant::Now();
        SharedData->Sync = 1;
        DoFutexWake(*(int*)(&SharedData->Sync), (int)processesCount);
        for (auto& pid: pids) {
            WaitNormalExit(pid);
        }
        const auto finish = TInstant::Now();
        UNIT_ASSERT_VALUES_EQUAL(SharedData->Counter, eachProcessCountTo * processesCount);
        Cout << "took [" << (finish - start).MilliSeconds() << "]" << Endl;
    }

    void TestKillInUnlock() {
        constexpr size_t iterationsCount = 1000;
        SharedData = CreateSharedData();
        for (size_t i = 0; i < iterationsCount; ++i) {
            ResetSharedData(SharedData);
            const pid_t pid1 = DoFork();
            if (pid1 == 0) {
                ResetThreadContext();
                AcquireSemiRobustMutex(SharedData->Mutex);
                ++SharedData->Counter;
                SharedData->Sync = 1;
                DoFutexWake(*(int*)(&SharedData->Sync), 1);
                DoFutexWait(*(int*)(&SharedData->Sync2), 0);
                ReleaseSemiRobustMutex(SharedData->Mutex);
                Sleep(TDuration::Hours(1));
                _Exit(0);
            }
            DoFutexWait(*(int*)(&SharedData->Sync), 0);
            const pid_t pid2 = DoFork();
            if (pid2 == 0) {
                ResetThreadContext();
                SharedData->Sync = 2;
                DoFutexWake(*(int*)(&SharedData->Sync), 1);
                AcquireSemiRobustMutex(SharedData->Mutex);
                ++SharedData->Counter;
                ReleaseSemiRobustMutex(SharedData->Mutex);
                _Exit(0);
            }
            DoFutexWait(*(int*)(&SharedData->Sync), 1);
            Sleep(TDuration::MilliSeconds(1));

            SharedData->Sync2 = 1;
            DoFutexWake(*(int*)(&SharedData->Sync2), 1);
            Sleep(TDuration::MilliSeconds(0));
            DoKill(pid1, SIGKILL);
            if (GetSemiRobustMutexOwnerPid(SharedData->Mutex) == (size_t)pid1) {
                ReleaseSemiRobustMutex(SharedData->Mutex);
                PulseSemiRobustMutex(SharedData->Mutex);
            }

            WaitSignaled(pid1, SIGKILL);
            WaitNormalExit(pid2);
            UNIT_ASSERT_VALUES_EQUAL(SharedData->Counter, 2);
        }
    }

private:
    static TSharedData* CreateSharedData() {
        int flags = MAP_SHARED | MAP_ANONYMOUS;
        int fd = -1;
        void* sharedData = DoMmap(nullptr, sizeof(TSharedData), PROT_READ | PROT_WRITE, flags, fd, 0);
        auto* result = static_cast<TSharedData*>(sharedData);
        ResetSharedData(result);
        return result;
    }

    static void DestroySharedData(TSharedData* sharedData) {
        DoMunmap(sharedData, sizeof(*sharedData));
    }

    static void WaitSignaled(int pid, int sig) {
        int status;
        const pid_t waitPidResult = DoWaitPid(pid, &status, 0);
        Y_VERIFY(waitPidResult == pid);
        Y_VERIFY(WIFSIGNALED(status) && WTERMSIG(status) == sig);
    }

    static void CheckAlive(pid_t pid) {
        int status;
        const pid_t processAlive = 0;
        const pid_t waitPidResult = DoWaitPid(pid, &status, WNOHANG);
        Y_VERIFY(waitPidResult == processAlive);
    }

    static size_t WaitAnyProcessNormalExit(TVector<pid_t>& pids) {
        while (true) {
            for (auto it = begin(pids); it != pids.end(); ++it) {
                if (CheckExitedNormally(*it)) {
                    size_t result = (size_t)(*it);
                    pids.erase(it);
                    return result;
                }
            }
            Sleep(TDuration::MilliSeconds(1));
        }
    }

    static bool CheckExitedNormally(pid_t pid) {
        int status;
        const pid_t processAlive = 0;
        const pid_t waitPidResult = DoWaitPid(pid, &status, WNOHANG);
        if (waitPidResult == processAlive) {
            return false;
        }
        Y_VERIFY(WIFEXITED(status));
        Y_VERIFY(WEXITSTATUS(status) == 0);
        return true;
    }

    static void WaitNormalExit(pid_t pid) {
        int status;
        const pid_t waitPidResult = DoWaitPid(pid, &status, 0);
        Y_VERIFY(waitPidResult == pid);
        Y_VERIFY(WIFEXITED(status));
        Y_VERIFY(WEXITSTATUS(status) == 0);
    }

    static void ResetSharedData(TSharedData* sharedData) {
        sharedData->Counter = 0;
        sharedData->Sync = 0;
        sharedData->Sync2 = 0;
        InitializeSemiRobustMutex(sharedData->Mutex);
    }

private:
    TSharedData* SharedData = nullptr;
};

UNIT_TEST_SUITE_REGISTRATION(TSemiRobustMutexTest);
