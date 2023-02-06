#include <robot/rthub/misc/io.h>

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/protobuf/util/pb_io.h>

#include <util/generic/buffer.h>
#include <util/system/mutex.h>

using namespace NRTHub;

template <typename TCallback>
class TIOCallback final: public IIOCallback {
public:
    TIOCallback(TCallback&& callback)
        : Callback(std::move(callback))
    {
    }

    void OnData(TBuffer& buffer) override {
        Callback(buffer);
    }

private:
    TCallback Callback;
};

template <typename TCallback>
THolder<IIOCallback> MakeIOCallback(TCallback&& callback){
    return MakeHolder<TIOCallback<TCallback>>(std::forward<TCallback>(callback));
}

class TIODispatcherTest final: public TTestBase {
private:
    UNIT_TEST_SUITE(TIODispatcherTest);
        UNIT_TEST(TestReadEvents);
        UNIT_TEST(TestReadWriteEvents);
        UNIT_TEST(TestHang);
        UNIT_TEST(TestExternalEvents);
    UNIT_TEST_SUITE_END();

    THolder<IIODispatcher> Dispatcher;
    TIOPool* Pool;

    void CreateConnection(const TFd& fd, EIODirection direction, IIOCallback& callback,
                          std::function<void(TConnectionParameters&)> modify = std::function<void(TConnectionParameters&)>()) {
        TConnectionParameters parameters;
        parameters.Direction = direction;
        parameters.Callback = &callback;
        parameters.Pool = Pool;
        if (modify) {
            modify(parameters);
        }
        Dispatcher->Listen(TFd(fd), parameters);
    }

public:
    void SetUp() override {
        Dispatcher = MakeIODispatcher();
        Pool = &Dispatcher->RegisterPool(1, 1000);
    };

    void TestReadEvents() {
        TPipe pipe;
        MakeNonblocking(pipe.Write);

        TStringBuilder logBuilder;
        std::atomic<ui32> events{0};

        auto readCallback = MakeIOCallback([&](TBuffer& buffer) {
            UNIT_ASSERT(buffer.Size() > 0);
            logBuilder << "read(" << TStringBuf(buffer.Data(), buffer.Size()) << ") ";
            ++events;
        });
        CreateConnection(pipe.Read, EIODirection::Read, *readCallback);

        auto notificationCallback = MakeIOCallback([&](TBuffer& buffer) {
            Y_VERIFY(buffer.Size() == sizeof(size_t));
            size_t notificationCount;
            memcpy(&notificationCount, buffer.Data(), sizeof(size_t));
            logBuilder << "notification(" << notificationCount << ") ";
            ++events;
        });
        TNotificationHandle notificationHandle;
        CreateConnection(notificationHandle.GetFd(), EIODirection::Read, *notificationCallback);

        Dispatcher->Start();
        {
            TString message("msg1");
            logBuilder << "write(" << message << ") ";
            DoWrite(pipe.Write.Unwrap(), message.data(), message.size());
            WaitEvents(events, 1);
        }
        {
            TString message("msg2");
            logBuilder << "write(" << message << ") ";
            DoWrite(pipe.Write.Unwrap(), message.data(), message.size());
            WaitEvents(events, 2);
        }
        {
            TString message("msg3");
            logBuilder << "write(" << message << ") ";
            DoWrite(pipe.Write.Unwrap(), message.data(), message.size());
            WaitEvents(events, 3);
        }
        notificationHandle.Raise();
        WaitEvents(events, 4);

        Dispatcher->Stop();
        UNIT_ASSERT_VALUES_EQUAL("write(msg1) read(msg1) write(msg2) read(msg2) write(msg3) read(msg3) notification(1) ", logBuilder);
    }

    void TestReadWriteEvents() {
        TPipe pipe;

        TStringBuilder writeLog;
        ui32 writeEventsCount = 0;

        auto writeCallback = MakeIOCallback([&](TBuffer& buffer) {
            if (writeEventsCount < 3) {
                TString message = Sprintf("msg%u", writeEventsCount);
                buffer.Append(message.data(), message.size());
                writeLog << "written(" << message << ") ";
                ++writeEventsCount;
            }
        });
        CreateConnection(pipe.Write, EIODirection::Write, *writeCallback);

        TStringBuilder readContent;
        TMutex readContentLock;
        auto readCallback = MakeIOCallback([&](TBuffer& buffer) {
            with_lock(readContentLock) {
                readContent << TStringBuf(buffer.Data(), buffer.Size());
            }
        });
        CreateConnection(pipe.Read, EIODirection::Read, *readCallback);

        Dispatcher->Start();

        Wait<TString>("msg0msg1msg2", [&]() {
            with_lock(readContentLock) {
                return TString(readContent);
            }
        });
        Dispatcher->Stop();

        UNIT_ASSERT_VALUES_EQUAL("written(msg0) written(msg1) written(msg2) ", writeLog);
    }

    void TestHang() {
        TPipe pipe;

        TStringBuilder logBuilder;
        std::atomic<ui32> events{0};

        auto readCallback = MakeIOCallback([&](TBuffer& buffer) {
            UNIT_ASSERT(buffer.Size() > 0);
            logBuilder << "read(" << TStringBuf(buffer.Data(), buffer.Size()) << ") ";
            ++events;
        });
        CreateConnection(pipe.Read, EIODirection::Read, *readCallback, [&](TConnectionParameters& parameters) {
            parameters.OnHang = [&]() {
                logBuilder << "hang() ";
                ++events;
            };
        });

        Dispatcher->Start();
        TString message("msg1");
        logBuilder << "write(" << message << ") ";
        DoWrite(pipe.Write.Unwrap(), message.data(), message.size());
        WaitEvents(events, 1);
        pipe.Write.Close();
        WaitEvents(events, 2);
        Dispatcher->Stop();

        UNIT_ASSERT_VALUES_EQUAL("write(msg1) read(msg1) hang() ", logBuilder);
    }

    void TestExternalEvents() {
        TPipe pipe;
        MakeNonblocking(pipe.Read);

        std::atomic<ui32> events{0};
        TString dataToWrite;

        auto writeCallback = MakeIOCallback([&](TBuffer& buffer) {
            if (!dataToWrite.empty()) {
                buffer.Append(dataToWrite.data(), dataToWrite.size());
                dataToWrite = "";
            }
            ++events;
        });
        TNotificationHandle dataAvailableSignal;
        CreateConnection(pipe.Write, EIODirection::Write, *writeCallback, [&](TConnectionParameters& parameters) {
            parameters.ExternalEventsSource = &dataAvailableSignal.GetFd();
        });

        Dispatcher->Start();
        WaitEvents(events, 1);
        {
            const size_t bufferSize = 100;
            char buffer[bufferSize];
            UNIT_ASSERT_VALUES_EQUAL(0, DoRead(pipe.Read.Unwrap(), buffer, bufferSize));
        }

        dataToWrite = "test-message";
        dataAvailableSignal.Raise();

        WaitEvents(events, 3);
        const TInstant deadline = TInstant::Now() + TDuration::Seconds(10);
        while (true) {
            Y_VERIFY(TInstant::Now() < deadline, "timeout waiting for message");
            const size_t bufferSize = 100;
            char buffer[bufferSize];
            const auto bytesRead = static_cast<size_t>(DoRead(pipe.Read.Unwrap(), buffer, bufferSize));
            if (bytesRead != 0) {
                TString value(buffer, bytesRead);
                UNIT_ASSERT_VALUES_EQUAL(value, "test-message");
                break;
            }
            Sleep(TDuration::MilliSeconds(3));
        }
        Dispatcher->Stop();
    }

private:
    void WaitEvents(std::atomic<ui32>& atomic, ui32 value) {
        Wait<ui32>(value, [&]() {
           return atomic.load();
        });
    }

    template <typename TValue, typename TGetter>
    void Wait(const TValue& expectedValue, TGetter&& getter) {
        const TInstant deadline = TInstant::Now() + TDuration::Seconds(10);
        TValue lastValue;
        while (true) {
            Y_VERIFY(TInstant::Now() < deadline, "timeout, last value [%s]", ToString(lastValue).c_str());
            lastValue = getter();
            if (lastValue == expectedValue) {
                break;
            }
            Sleep(TDuration::MilliSeconds(3));
        }
    }
};

UNIT_TEST_SUITE_REGISTRATION(TIODispatcherTest);
