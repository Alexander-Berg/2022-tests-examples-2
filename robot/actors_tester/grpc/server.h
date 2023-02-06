#pragma once

#include <robot/zora/tools/actors_tester/grpc/proto/proto.pb.h>
#include <robot/zora/tools/actors_tester/grpc/proto/proto.grpc.pb.h>

#include <contrib/libs/grpc/include/grpc++/grpc++.h>

#include <util/generic/ptr.h>
#include <util/system/thread.h>
#include <util/datetime/base.h>

class TGrpcServer final {
public:
    using TCallback = std::function<void(NAsyncGrpcTest::Request request)>;
    TGrpcServer(TString uri);
    ~TGrpcServer();

    void Start();
    void SetCallback(TCallback cb); //TODO: need to associate types of requests to callbacks

private:

    class CallData {
    public:
        CallData(NAsyncGrpcTest::TestService::AsyncService* service, grpc::ServerCompletionQueue* cq, TCallback& callback);

        void Proceed();

    private:
        NAsyncGrpcTest::TestService::AsyncService* Service;
        grpc::ServerCompletionQueue* Cq;
        grpc::ServerContext Ctx;

        NAsyncGrpcTest::Request Request;
        NAsyncGrpcTest::Response Response;

        grpc::ServerAsyncResponseWriter<NAsyncGrpcTest::Response> Responder;

        enum CallStatus { CREATE, PROCESS, FINISH };
        CallStatus Status;
        TCallback& Callback;
    };

     void HandleRpcs();

    std::unique_ptr<grpc::ServerCompletionQueue> Cq;
    NAsyncGrpcTest::TestService::AsyncService Service;
    std::unique_ptr<grpc::Server> Server;

    TSimpleSharedPtr<TThread> Thread;
    TString Uri;
    TCallback Callback;
};
