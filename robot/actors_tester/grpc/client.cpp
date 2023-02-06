#include "client.h"


TGrpcClient::TGrpcClient(TString uri) :
    Channel(grpc::CreateChannel(uri, grpc::InsecureChannelCredentials()))
  , Stub(NAsyncGrpcTest::TestService::NewStub(Channel))
  , cq()
{
}

void TGrpcClient::Start() {
    Thread.Reset(MakeSimpleShared<TThread>([this](){
        void* tag;
        bool ok;
        while (cq.Next(&tag, &ok)) {
            if (!ok) {
                //TODO
            }
            AsyncClientCall* clientCall = static_cast<AsyncClientCall*>(tag);
            try {
//                Cerr << clientCall->Status.ok();
//                Cerr << " " << clientCall->Status.error_details();
//                Cerr << " " << clientCall->Status.error_message() << Endl;
                clientCall->Cb(ok, clientCall->Reply, TString(clientCall->Status.error_message()));
            } catch (...) {
                //TODO
            }
            delete clientCall;
        }
    }));
    Thread->Start();
}

void TGrpcClient::GetResponse(TString data, TGrpcClient::TCallback cb) {
    NAsyncGrpcTest::Request request;
    request.SetSomeData(data);

    AsyncClientCall* call = new AsyncClientCall(cb);
    call->ResponseReader = Stub->PrepareAsyncGetResponse(&call->Context, request, &cq);

    call->ResponseReader->StartCall();

    call->ResponseReader->Finish(&call->Reply, &call->Status, (void*)call);
}
