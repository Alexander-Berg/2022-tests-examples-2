#include <robot/zora/tools/async_grpc_test/proto/proto.pb.h>
#include <robot/zora/tools/async_grpc_test/proto/proto.grpc.pb.h>

#include <contrib/libs/grpc/include/grpc++/grpc++.h>

#include <util/generic/ptr.h>


class ServerImpl final {
public:
    ~ServerImpl() {
        Server->Shutdown();
        Cq->Shutdown();
    }
    
    void Run() {
        std::string server_address("0.0.0.0:50051");
        
        grpc::ServerBuilder builder;
        builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
        builder.RegisterService(&Service);
        Cq = builder.AddCompletionQueue();
        Server = builder.BuildAndStart();
        Cerr << "Server listening on " << server_address << Endl;
        
        // Proceed to the server's main loop.
        HandleRpcs();
    }
    
private:
    class CallData {
    public:
        CallData(NGrpcTest::TestService::AsyncService* service, grpc::ServerCompletionQueue* cq)
            : Service(service), Cq(cq), Responder(&Ctx), Status(CREATE) {
            Proceed();
        }

        void Proceed() {
            if (Status == CREATE) {
                Status = PROCESS;
                Service->RequestGetResponse(&Ctx, &Request, &Responder, Cq, Cq, this);
                Cerr << "Create" << Endl;

            } else if (Status == PROCESS) {
                new CallData(Service, Cq);

                TString prefix("Hello ");
                Response.SetSomeData(prefix + Request.GetSomeData());

                Status = FINISH;
                Cerr << "Process" << Endl;
                Responder.Finish(Response, grpc::Status::OK, this);

            } else {
                assert(Status == FINISH);
                delete this;
            }
        }

    private:
        NGrpcTest::TestService::AsyncService* Service;
        grpc::ServerCompletionQueue* Cq;
        grpc::ServerContext Ctx;

        NGrpcTest::Request Request;
        NGrpcTest::Response Response;

        grpc::ServerAsyncResponseWriter<NGrpcTest::Response> Responder;

        enum CallStatus { CREATE, PROCESS, FINISH };
        CallStatus Status;
    };

     void HandleRpcs() {
       new CallData(&Service, Cq.get());
       void* tag;  // uniquely identifies a request.
       bool ok;
       while (true) {
         assert(Cq->Next(&tag, &ok));
         assert(ok);
         static_cast<CallData*>(tag)->Proceed();
       }
     }
    
    std::unique_ptr<grpc::ServerCompletionQueue> Cq;
    NGrpcTest::TestService::AsyncService Service;
    std::unique_ptr<grpc::Server> Server;
};


int main(int, char**) {
    ServerImpl server;
    server.Run();

    return 0;
}
