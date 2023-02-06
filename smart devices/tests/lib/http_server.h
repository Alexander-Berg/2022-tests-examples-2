#pragma once

#include <library/cpp/http/server/http.h>
#include <library/cpp/http/server/response.h>
#include <library/cpp/http/misc/parsed_request.h>
#include <library/cpp/http/fetch/exthttpcodes.h>

namespace IOUpdater {
    class TestHTTPServer: public THttpServer, public THttpServer::ICallBack {
    public:
        using THandler = std::function<THttpResponse()>;

        TestHTTPServer();
        ~TestHTTPServer() override;

        void addHandler(TString path, THandler resp);
        const TString& address() const noexcept;

    private:
        using THandlers = std::vector<std::pair<TString, THandler>>;
        THandlers handlers_;
        TString address_;

        TClientRequest* CreateClient() override;
    };
} // namespace IOUpdater
