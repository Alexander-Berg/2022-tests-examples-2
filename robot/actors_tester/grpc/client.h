#pragma once

#include <robot/zora/tools/actors_tester/grpc/proto/proto.pb.h>
#include <robot/zora/tools/actors_tester/grpc/proto/proto.grpc.pb.h>

#include <contrib/libs/grpc/include/grpc++/grpc++.h>

#include <util/generic/ptr.h>
#include <util/system/thread.h>
#include <util/datetime/base.h>


class TGrpcClient {
public:
//    using TCallback = void(*)(bool ok, NAsyncGrpcTest::Response response);
//    using TCallback = std::function<void(bool ok, NAsyncGrpcTest::Response response, TString error_message)>;
    using TCallback = std::function<void(bool ok, NAsyncGrpcTest::Response response, TString error_message)>;
private:
    struct AsyncClientCall {
        AsyncClientCall(TCallback cb) : Cb(cb) {}
        NAsyncGrpcTest::Response Reply;

        grpc::ClientContext Context;

        grpc::Status Status;

        std::unique_ptr<grpc::ClientAsyncResponseReader<NAsyncGrpcTest::Response>> ResponseReader;

        TCallback Cb;
    };

public:
    TGrpcClient(TString uri);

    void Start();

    void GetResponse(TString data, TCallback cb);

private:
    std::shared_ptr<grpc::Channel> Channel;
    std::unique_ptr<NAsyncGrpcTest::TestService::Stub> Stub;

    TSimpleSharedPtr<TThread> Thread;
    grpc::CompletionQueue cq;
};
