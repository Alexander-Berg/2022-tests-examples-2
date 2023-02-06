#include <robot/rthub/misc/message_transport.h>
#include <robot/rthub/misc/system.h>

#include <library/cpp/testing/unittest/registar.h>

#include <util/random/random.h>
#include <util/system/mutex.h>

using namespace NRTHub;

struct TTestStringMessage {
    size_t SequenceNumber;
    TString Content;

    void Save(IOutputStream* target) const {
        ::Save(target, SequenceNumber);
        ::Save(target, Content);
    }

    void Load(IInputStream* source) {
        ::Load(source, SequenceNumber);
        ::Load(source, Content);
    }

    static const ui64 TransportId = 1;
};

struct TTestIntMessage {
    size_t SequenceNumber;
    int Content;

    void Save(IOutputStream* target) const {
        ::Save(target, SequenceNumber);
        ::Save(target, Content);
    }

    void Load(IInputStream* source) {
        ::Load(source, SequenceNumber);
        ::Load(source, Content);
    }

    static const ui64 TransportId = 2;
};

struct TEmptyMessage {
    void Save(IOutputStream*) const {
    }

    void Load(IInputStream*) {
    }

    static const ui64 TransportId = 3;
};

class TMessageTransportTest: public TTestBase {
private:
    UNIT_TEST_SUITE(TMessageTransportTest)
    UNIT_TEST(TestSimple)
    UNIT_TEST(TestSkipGarbage)
    UNIT_TEST(TestCanDeliverEmptyMessage)
    UNIT_TEST(TestRandomized)
    UNIT_TEST_SUITE_END();
public:
    static const size_t BufferSize;

    void SetUp() override {
        Pipe = MakeHolder<TPipe>();
        Y_VERIFY(BufferSize < PIPE_BUF);
        MessageTransport = MakeHolder<TMessageTransport>(ULL(1), ULL(1), BufferSize);
        MessageEndpoint = MessageTransport->CreateEndpoint(TLink{TFd(Pipe->Read), TFd(Pipe->Write)}, []() { });
    }

    void TearDown() override {
        MessageTransport->Stop();
        MessageEndpoint.Destroy();
        MessageTransport.Destroy();
        Pipe.Destroy();
    }

    void TestSimple() {
        TManualEvent handlerCalled;
        MessageEndpoint->OnReceive<TTestStringMessage>([&](TTestStringMessage&& message) {
            UNIT_ASSERT_VALUES_EQUAL("test-message-content", message.Content);
            handlerCalled.Signal();
        });
        MessageTransport->Start();
        MessageEndpoint->SendOrDie<TTestStringMessage>({0, "test-message-content"});
        UNIT_ASSERT(handlerCalled.WaitT(TDuration::Seconds(1)));
    }

    void TestSkipGarbage() {
        TStringBuilder receivedMessages;
        TMutex lock;
        MessageEndpoint->OnReceive<TTestStringMessage>([&](TTestStringMessage&& message) {
            with_lock(lock) {
                receivedMessages << message.Content << " ";
            }
        });
        MessageTransport->Start();
        MessageEndpoint->SendOrDie<TTestStringMessage>({0, "test-message1"});
        {
            const TString garbage = GenerateRandomString();
            DoWrite(Pipe->Write.Unwrap(), garbage.data(), garbage.size());
        }
        MessageEndpoint->SendOrDie<TTestStringMessage>({0, "test-message2"});
        Wait([&]() {
            with_lock(lock) {
                return receivedMessages == "test-message1 test-message2 ";
            }
        }, TDuration::Seconds(10));
    }

    void TestCanDeliverEmptyMessage() {
        TManualEvent handlerCalled;
        MessageEndpoint->OnReceive<TEmptyMessage>([&handlerCalled](auto&&) {
            handlerCalled.Signal();
        });
        MessageTransport->Start();
        MessageEndpoint->SendOrDie<TEmptyMessage>({});
        UNIT_ASSERT(handlerCalled.WaitT(TDuration::Seconds(1)));
    }

    void TestRandomized() {
        TVector<TString> sentMessages;
        TVector<TString> receivedMessages;
        TAtomic stopReceived = 0;

        MessageEndpoint->OnReceive<TTestStringMessage>([&](auto&& message) {
            receivedMessages.push_back(Sprintf("TTestStringMessage(%lu, %s)",
                                               message.SequenceNumber, message.Content.c_str()));
            if (message.Content == "stop") {
                AtomicSet(stopReceived, 1);
            }
        });
        MessageEndpoint->OnReceive<TTestIntMessage>([&](auto&& message) {
            receivedMessages.push_back(Sprintf("TTestIntMessage(%lu, %d)",
                                               message.SequenceNumber, message.Content));
        });
        MessageTransport->Start();
        const size_t testMessagesCount = 100000;
        for (size_t i = 0; i < testMessagesCount; ++i) {
            if (RandomNumber<double>() < 0.3) {
                const TString garbage = GenerateRandomString();

                //запись атомарна (BufferSize < PIPE_BUF), но может
                //сломать сообщение, если вклинится между блоками
                DoWrite(Pipe->Write.Unwrap(), garbage.data(), garbage.size());
            }
            if (RandomNumber<double>() < 0.5) {
                const int value = static_cast<int>(RandomNumber<ui32>());
                MessageEndpoint->SendOrDie(TTestIntMessage{i, value});
                sentMessages.push_back(Sprintf("TTestIntMessage(%lu, %d)", i, value));
            } else {
                const TString value = GenerateRandomString();
                MessageEndpoint->SendOrDie(TTestStringMessage{i, value});
                sentMessages.push_back(Sprintf("TTestStringMessage(%lu, %s)", i, value.c_str()));
            }
        }

        MessageEndpoint->SendOrDie(TTestStringMessage{testMessagesCount, "stop"});
        sentMessages.push_back(Sprintf("TTestStringMessage(%lu, %s)", testMessagesCount, "stop"));
        Wait([&]() { return AtomicGet(stopReceived) == 1; }, TDuration::Seconds(10));

        size_t receivedMessageIndex = 0;
        bool canMismatch = false;
        ui64 lostMessages = 0;
        for (const TString& sent: sentMessages) {
            const bool matched = sent == receivedMessages[receivedMessageIndex];
            if (matched) {
                canMismatch = true;
                ++receivedMessageIndex;
            } else {
                UNIT_ASSERT(canMismatch);
                ++lostMessages;
                canMismatch = false;
            }
        }
        UNIT_ASSERT_VALUES_EQUAL(receivedMessageIndex, receivedMessages.size());
        UNIT_ASSERT(lostMessages < MessageEndpoint->GetTotalBytesSent() / BufferSize);
    }

private:
    template <typename TCondition>
    void Wait(TCondition condition, TDuration timeout) {
        const TInstant timeoutAt = TInstant::Now() + timeout;
        while (true) {
            UNIT_ASSERT_C(TInstant::Now() < timeoutAt, "timeout");
            if (condition()) {
                break;
            }
            Sleep(TDuration::MilliSeconds(3));
        }
    }

    TString GenerateRandomString() {
        const ui32 size = RandomNumber<ui32>(100);
        TString result;
        for (size_t j = 0; j < size; ++j) {
            result.append(RandomNumber<char>());
        }
        return result;
    }

private:
    THolder<TPipe> Pipe;
    THolder<TMessageTransport> MessageTransport;
    THolder<TMessageEndpoint> MessageEndpoint;
};

const size_t TMessageTransportTest::BufferSize = 512;

UNIT_TEST_SUITE_REGISTRATION(TMessageTransportTest);
