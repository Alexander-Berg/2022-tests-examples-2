#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/tests_data.h>
#include <library/cpp/testing/unittest/registar.h>
#include <util/string/builder.h>

#include <smart_devices/tools/updater/logging/utils.h>

#include "http_server.h"

namespace IOUpdater {

    TestHTTPServer::TestHTTPServer()
        : THttpServer{this, TOptions(TPortManager{}.GetTcpPort()).AddBindAddress("localhost")}
    {
        address_ = TStringBuilder() << "http://localhost:" << Options().Port;
        Start();
    }

    TestHTTPServer::~TestHTTPServer() {
        Stop();
    }

    void TestHTTPServer::addHandler(TString path, THandler resp) {
        handlers_.erase(std::remove_if(handlers_.begin(), handlers_.end(), [&path](std::pair<TString, THandler>& p) { return p.first == path; }),
                        handlers_.end());
        handlers_.emplace_back(path, resp);
    }

    const TString& TestHTTPServer::address() const noexcept {
        return address_;
    }

    TClientRequest* TestHTTPServer::CreateClient() {
        struct TReplier: public TRequestReplier {
            explicit TReplier(const THandlers& handlers)
                : Handlers_{handlers}
            {
            }

            bool DoReply(const TReplyParams& r) override {
                TParsedHttpRequest req{r.Input.FirstLine()};

                TStringStream headersFormatted{};
                r.Input.Headers().OutTo(&headersFormatted);
                SPDLOG_INFO("Request: {}", r.Input.FirstLine());
                SPDLOG_INFO("Request headers: {}", headersFormatted.Data());

                auto it = std::find_if(Handlers_.cbegin(), Handlers_.cend(),
                                       [&](const std::pair<TString, THandler>& urlHandler) { return req.Request.starts_with(urlHandler.first); });
                if (it == Handlers_.end()) {
                    UNIT_FAIL("Unknown handler request: " << req.Request);
                }

                TStringStream reply;
                reply << it->second();

                r.Output << reply.Data();

                headersFormatted.clear();
                r.Output.SentHeaders().OutTo(&headersFormatted);
                UPDATER_LOG_DEBUG("Reply headers: {}", headersFormatted.Data());
                UPDATER_LOG_DEBUG("Reply body: {}", reply.Data());
                return true;
            }

            const THandlers& Handlers_;
        };

        return new TReplier{handlers_};
    }

} // namespace IOUpdater
