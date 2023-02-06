#include <robot/zora/tools/async_grpc_test/proto/proto.pb.h>
#include <robot/zora/tools/async_grpc_test/proto/proto.grpc.pb.h>

#include <contrib/libs/grpc/include/grpc++/grpc++.h>

#include <util/generic/ptr.h>
#include <util/system/thread.h>
#include <util/datetime/base.h>


class TGrpcClient {
public:
    using TCallback = void(*)(bool ok, NGrpcTest::Response response);
private:
    struct AsyncClientCall {
        AsyncClientCall(TCallback cb) : Cb(cb) {}
        NGrpcTest::Response Reply;

        grpc::ClientContext Context;

        grpc::Status Status;

        std::unique_ptr<grpc::ClientAsyncResponseReader<NGrpcTest::Response>> ResponseReader;

        TCallback Cb;
    };

public:
    TGrpcClient(TString uri) :
        Channel(grpc::CreateChannel(uri, grpc::InsecureChannelCredentials()))
        , Stub(NGrpcTest::TestService::NewStub(Channel))
        , cq()
    {
    }

    void Start() {
        Thread.Reset(MakeSimpleShared<TThread>([this](){
            void* tag;
            bool ok;
            while (cq.Next(&tag, &ok)) {
                AsyncClientCall* clientCall = static_cast<AsyncClientCall*>(tag);
//                try {
                    clientCall->Cb(ok, clientCall->Reply);
//                    delete clientCall;
//                } catch (...) {
//                }
            }
        }));
        Thread->Start();
    }

    void GetResponse(TString data, TCallback cb) {
        NGrpcTest::Request request;
        request.SetSomeData(data);

        AsyncClientCall* call = new AsyncClientCall(cb);
        call->ResponseReader = Stub->PrepareAsyncGetResponse(&call->Context, request, &cq);

        call->ResponseReader->StartCall();

        call->ResponseReader->Finish(&call->Reply, &call->Status, (void*)call);
        Cerr << "GetResponse" << Endl;
    }

private:
    std::shared_ptr<grpc::Channel> Channel;
    std::unique_ptr<NGrpcTest::TestService::Stub> Stub;

    TSimpleSharedPtr<TThread> Thread;
    grpc::CompletionQueue cq;
};




void printReply(bool ok, NGrpcTest::Response response) {
    if (ok) {
        Cerr << response.GetSomeData() << Endl;
    } else {
        Cerr << "RPC failed" << Endl;
    }
}

int main() {
    TGrpcClient client("0.0.0.0:50051");
    for (int i = 0; i < 10; ++i) {
        client.GetResponse("ololo", &printReply);
    }
    client.Start();
    Sleep(TDuration::MicroSeconds(10000000));
    return 0;
}
