#include "bob_handler.h"
#include "client.h"
#include "server.h"

#include <library/cpp/testing/common/network.h>
#include <library/cpp/testing/unittest/registar.h>

#include <util/generic/hash_set.h>
#include <util/string/cast.h>
#include <util/string/vector.h>
#include <util/system/mutex.h>

using namespace NZora;

class TGrpcTester : public TTestBase {
    UNIT_TEST_SUITE(TGrpcTester)
    UNIT_TEST(TestGrpc)
    UNIT_TEST_SUITE_END();

public:
    void TestGrpc();

private:
    void Init(TString port);

    void StartServer();
    void StopServer();

    void StartClient();
    void StopClient();
    void RecreateClient();

private:
    TString Uri;

    THolder<TTestServer> Server;

    TCompletionQueuePoller ClientPoller;
    THolder<TTestClient> Client;
};

UNIT_TEST_SUITE_REGISTRATION(TGrpcTester)


void TGrpcTester::Init(TString port) {
    Uri = "127.0.0.1:" + port;
}

void TGrpcTester::StartServer() {
    TGrpcServerConfig config {
        .ListenUri = Uri
    };
    Server = MakeHolder<TTestServer>(config);

    Server->RegisterCallHandler(MakeHolder<TSendFastMessageHandler>());
    Server->RegisterCallHandler(MakeHolder<TBobHandler>());

    Server->Start();
}

void TGrpcTester::StopServer() {
    Server->Stop(false);
}


void TGrpcTester::StartClient() {
    ClientPoller.Start();
    Client = MakeHolder<TTestClient>(Uri, ClientPoller.GetQueue());
}

void TGrpcTester::StopClient() {
    Client.Reset();
}

void TGrpcTester::RecreateClient() {
    Client = MakeHolder<TTestClient>(Uri, ClientPoller.GetQueue());
}


void WaitForRequests(int requests, TDuration maxWait = TDuration::Seconds(5)) {
    auto finish = TInstant::Now() + maxWait;
    while (TInstant::Now() < finish) {
        if (TSendFastMessageHandler::RequestsAmount == requests) {
            return;
        }
        Sleep(TDuration::MilliSeconds(100));
    }
    ZLogError("Unexpected number of requests") << "Expected: " << requests << "; got: " << TSendFastMessageHandler::RequestsAmount;
    Y_FAIL("Unexpected number of requests; see stderr/stdout");
}

TAliceRequest CraeteRequest(const TString& msg) {
    TAliceRequest data;
    data.SetMessage(msg);
    return data;
}

TAliceResponse CraeteResponse(const TString& msg) {
    TAliceResponse data;
    data.SetAnswer(msg);
    return data;
}

TAtomic Answers = 0;

auto CreateChecknigCallback(const TString& result) {
    return [result](bool ok, TAliceResponse&& resp, const grpc::Status& status) {
        ++Answers;
        UNIT_ASSERT_C(ok && status.ok(), ToString<int>(status.error_code()) + " " + status.error_message());
        UNIT_ASSERT_C(resp.GetAnswer() == result, "Unexpected answer; got " + resp.GetAnswer() + " expected " + result);
    };
}

// START OF TESTS

void TGrpcTester::TestGrpc() {
    auto port = NTesting::GetFreePort();
    Init(ToString(port));

    ZLogInfo("Starting server");
    StartServer();

    ZLogInfo("Starting client");
    StartClient();

    {
        ZLogInfo("Testing Bob request");
        TBobHandler::RequestsAmount = 0;
        Answers = 0;

        TBobRequest request;
        request.SetIndex(1);
        request.SetMessage("Hi!");
        Client->DoBobRequest(
            std::move(request),
            [](bool ok, TBobResponse&& resp, const grpc::Status& status) {
                ++Answers;
                UNIT_ASSERT_C(ok && status.ok(), ToString<int>(status.error_code()) + " " + status.error_message());
                UNIT_ASSERT_C(resp.GetAnswer() == "Bob answer #1: Hi!", "Unexpected answer");
            }
        );

        // bob is answering instantly, so we just need to wait for request and response
        Sleep(TDuration::Seconds(1));
        UNIT_ASSERT(Answers == 1);
    }

    {
        ZLogInfo("Testing ordinar request");
        TSendFastMessageHandler::RequestsAmount = 0;
        Answers = 0;
        Client->DoAliceRequest(
            CraeteRequest("Hi!"),
            [](bool ok, TAliceResponse&& resp, const grpc::Status& status) {
                ++Answers;
                UNIT_ASSERT_C(ok && status.ok(), ToString<int>(status.error_code()) + " " + status.error_message());
                UNIT_ASSERT_C(resp.GetAnswer() == "Hello!", "Unexpected answer");
            }
        );

        WaitForRequests(1);

        UNIT_ASSERT(TSendFastMessageHandler::Responders.contains("Hi!"));
        TSendFastMessageHandler::Responders["Hi!"]->Write(CraeteResponse("Hello!"));
        TSendFastMessageHandler::Responders.erase("Hi!");

        // waiting for answer
        Sleep(TDuration::Seconds(1));
        UNIT_ASSERT(Answers == 1);
    }


    {
        // many ordinar requests
        ZLogInfo("Testing many requests");
        TSendFastMessageHandler::RequestsAmount = 0;
        Answers = 0;
        static constexpr size_t requestsNum = 10;

        for (size_t i = 1; i < requestsNum + 1; ++i) {
            TString label = ToString<size_t>(i);
            Client->DoAliceRequest(
                CraeteRequest(label),
                CreateChecknigCallback("Answer: " + label)
            );
        }

        WaitForRequests(requestsNum);

        // in revert order
        for (size_t i = requestsNum; i > 0; --i) {
            TString label = ToString<size_t>(i);

            UNIT_ASSERT(TSendFastMessageHandler::Responders.contains(label));
            TSendFastMessageHandler::Responders[label]->Write(CraeteResponse("Answer: " + label));
            TSendFastMessageHandler::Responders.erase(label);
        }

        // waiting for answer
        Sleep(TDuration::Seconds(1));
        UNIT_ASSERT(Answers == requestsNum);
    }

    {
        ZLogInfo("Testing recreate client");
        RecreateClient();
        TSendFastMessageHandler::RequestsAmount = 0;
        Answers = 0;
        Client->DoAliceRequest(
            CraeteRequest("Hi!"),
            [](bool ok, TAliceResponse&& resp, const grpc::Status& status) {
                ++Answers;
                UNIT_ASSERT(ok && status.ok());
                UNIT_ASSERT_C(resp.GetAnswer() == "Hello!", "Unexpected answer");
            }
        );

        WaitForRequests(1);

        UNIT_ASSERT(TSendFastMessageHandler::Responders.contains("Hi!"));
        TSendFastMessageHandler::Responders["Hi!"]->Write(CraeteResponse("Hello!"));
        TSendFastMessageHandler::Responders.erase("Hi!");

        // waiting for answer
        Sleep(TDuration::Seconds(1));
        UNIT_ASSERT(Answers == 1);
    }

    {
        ZLogInfo("Testing hard server reset");
        TSendFastMessageHandler::RequestsAmount = 0;
        Answers = 0;
        Client->DoAliceRequest(
            CraeteRequest("Hi!"),
            [](bool ok, TAliceResponse&& resp, const grpc::Status& status) {
                ++Answers;
                UNIT_ASSERT_C(!ok && IsNetworkError(status), (ok ? "ok; " : "not ok; ") + ToString<int>(status.error_code()) + " " + status.error_message());
                Y_UNUSED(resp);
            }
        );

        WaitForRequests(1);

        Server->Stop(true);

        TSendFastMessageHandler::Responders["Hi!"]->Forget();
        TSendFastMessageHandler::Responders.erase("Hi!");

        // waiting for answer
        Sleep(TDuration::Seconds(1));
        UNIT_ASSERT(Answers == 1);
    }

    {
        ZLogInfo("Testing after hard server reset");
        // RecreateClient();
        TSendFastMessageHandler::RequestsAmount = 0;
        Answers = 0;
        Client->DoAliceRequest(
            CraeteRequest("Hi!"),
            [](bool ok, TAliceResponse&& resp, const grpc::Status& status) {
                ++Answers;
                UNIT_ASSERT_C(!ok && IsNetworkError(status), (ok ? "ok; " : "not ok; ") + ToString<int>(status.error_code()) + " " + status.error_message());
                Y_UNUSED(resp);
            }
        );

        // waiting for answer
        Sleep(TDuration::Seconds(1));
        UNIT_ASSERT(Answers == 1);
    }

    {
        ZLogInfo("Testing unexisting port");
        auto wrongPort = NTesting::GetFreePort();
        TString wrongUri = "127.0.0.1:" + ToString(wrongPort);

        auto new_client = MakeHolder<TTestClient>(wrongUri, ClientPoller.GetQueue());

        Answers = 0;
        new_client->DoAliceRequest(
            CraeteRequest("Hi!"),
            [](bool ok, TAliceResponse&& resp, const grpc::Status& status) {
                ++Answers;
                UNIT_ASSERT(!ok && IsNetworkError(status));
                Y_UNUSED(resp);
            }
        );

        Sleep(TDuration::Seconds(1));
        UNIT_ASSERT(Answers == 1);
    }

    ZLogInfo("Stopping all");
    StopClient();
    ClientPoller.Stop();
    // StopServer();    //was already stopped in test
    ZLogInfo("All is stopped");
}

