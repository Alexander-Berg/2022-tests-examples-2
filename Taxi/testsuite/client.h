#pragma once

#include "config.h"
#include <taxi/logistic-dispatcher/common_server/util/auto_actualization.h>

class TTestsuiteClient {
public:
    TTestsuiteClient(const TTestsuiteClientConfig& config)
        : Config(config)
        , AD(new TAsyncDelivery())
        , Agent(new NNeh::THttpClient(AD))
    {
        AD->Start(Config.GetRequestConfig().GetThreadsStatusChecker(), Config.GetRequestConfig().GetThreadsSenders());
        Agent->RegisterSource("testsuite-client", Config.GetHost(), Config.GetPort(), Config.GetRequestConfig(), Config.IsHttps());
    }

    virtual ~TTestsuiteClient() {
        AD->Stop();
    }

    NJson::TJsonValue Testpoint(const TString& name, const NJson::TJsonValue &value) const;

private:
    TTestsuiteClientConfig Config;
    TAtomicSharedPtr<TAsyncDelivery> AD;
    THolder<NNeh::THttpClient> Agent;
};
