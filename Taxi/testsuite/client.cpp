#include "client.h"

#include <taxi/logistic-dispatcher/library/tvm_services/abstract/client.h>
#include <taxi/logistic-dispatcher/util/json/json.h>

namespace {
class TestpointRequest: public NExternalAPI::IHttpRequestWithJsonReport {

  public:
    class TResponse: public IHttpRequestWithJsonReport::TResponse {
      public:
      protected:
        virtual bool DoParseJsonReply(const NJson::TJsonValue& jsonReply) override;
    };
    virtual bool BuildHttpRequest(NNeh::THttpRequest& request) const override;
};

}

NJson::TJsonValue TTestsuiteClient::Testpoint(const TString& name, const NJson::TJsonValue &value) const {
    NJson::TJsonValue payload;
    payload["name"] = name;
    payload["data"] = value;
    NNeh::THttpRequest request;
    request
        .SetUri(Config.GetRoute())
        .SetPostData(payload.GetStringRobust())
        .SetRequestType("POST")
        .AddHeader("Content-Type", "application/json");

    auto reply = Agent->SendMessageSync(request);
    if (reply.Code() != 200) {
        ERROR_LOG << "Testpoint finished with code " << reply.Code() << Endl;
        return {};
    }

    NJson::TJsonValue replyJson;
    if (!NJson::ReadJsonFastTree(reply.Content(), &replyJson)) {
        ERROR_LOG << "failed to parse testpoint response" << Endl;
        return {};
    }
    return replyJson["data"];
}
