#include "server.h"


TGrpcServer::TGrpcServer(TString uri) : Uri(uri) {}

TGrpcServer::~TGrpcServer() {
    Server->Shutdown();
    Cq->Shutdown();
}

void TGrpcServer::Start() {
    grpc::ServerBuilder builder;
    builder.AddListeningPort(Uri, grpc::InsecureServerCredentials());
    builder.RegisterService(&Service);
    Cq = builder.AddCompletionQueue();
    Server = builder.BuildAndStart();
    Cerr << "Server listening on " << Uri << Endl;

    // Proceed to the server's main loop.
    Thread.Reset(MakeSimpleShared<TThread>([this](){
        HandleRpcs();
    }));
}

void TGrpcServer::SetCallback(TGrpcServer::TCallback cb)
{
    Callback = cb;
}

void TGrpcServer::HandleRpcs() {
    new CallData(&Service, Cq.get(), Callback);
    void* tag = nullptr;  // uniquely identifies a request.
    bool ok = false;
    while (ok) {
        assert(Cq->Next(&tag, &ok));
        static_cast<CallData*>(tag)->Proceed();
    }
}

TGrpcServer::CallData::CallData(NAsyncGrpcTest::TestService::AsyncService *service, grpc::ServerCompletionQueue *cq, TCallback &callback)
    : Service(service), Cq(cq), Responder(&Ctx), Status(CREATE), Callback(callback) {
    Proceed();
}

void TGrpcServer::CallData::Proceed() {
    if (Status == CREATE) {
        Status = PROCESS;
        Service->RequestGetResponse(&Ctx, &Request, &Responder, Cq, Cq, this);

    } else if (Status == PROCESS) {
        new CallData(Service, Cq, Callback);

        TString prefix("Hello ");
        Response.SetSomeData(prefix + Request.GetSomeData());

        Status = FINISH;
        Responder.Finish(Response, grpc::Status::OK, this);
//        try { //TODO
        Callback(Request);
//        } catch (...) {
//        }
    } else {
        assert(Status == FINISH);
        delete this;
    }
}
