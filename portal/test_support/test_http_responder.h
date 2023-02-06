#pragma once

#include <portal/morda/blocks/core/net/http_client.h>

#include <util/generic/map.h>
#include <util/generic/string.h>
#include <util/generic/vector.h>
#include <util/system/mutex.h>

#include <memory>

namespace NJson {
    class TJsonValue;
} // namespace NJson

namespace NMordaBlocks {

    class TScopedTasksSequenceRunnerBase;

    class TTestHttpResponder : public TNonCopyable {
    public:
        class TTestHttpResourceResponder : public TNonCopyable {
        public:
            TTestHttpResourceResponder(TTestHttpResponder* responder, const TString& httpResourceId);
            ~TTestHttpResourceResponder();

            bool IsHttpRequestStarted() const;
            void WaitHttpRequest() const;
            const THttpRequest& GetRequest();

            THttpRequest SendResponse(std::unique_ptr<THttpResponse> response);
            THttpRequest SendResponse(int statusCode, TStringBuf data, TVector<TString> additionalHeaders);
            THttpRequest SendRawResponse(TStringBuf rawResponse);
            THttpRequest SendStatusCode(int statusCode);
            THttpRequest SendOkData(TStringBuf data);
            THttpRequest SendOkJson(const NJson::TJsonValue& json);

            void AutoSendRepeatedlyOkData(TString data);
            void ResetAutoSendingResource();

        private:
            TTestHttpResponder* Responder_;
            TString HttpResourceId_;
        };

        TTestHttpResponder();
        ~TTestHttpResponder();

        std::unique_ptr<TTestHttpResourceResponder> MakeResourceResponder(const TString& httpResourceId);

        bool IsHttpRequestStarted(const TString& httpResourceId) const;
        void WaitHttpRequest(const TString& httpResourceId) const;
        const THttpRequest& GetRequest(const TString& httpResourceId);

        THttpRequest SendResponse(const TString& httpResourceId, std::unique_ptr<THttpResponse> response);
        THttpRequest SendResponse(const TString& httpResourceId, int statusCode, TStringBuf data, TVector<TString> additionalHeaders);
        THttpRequest SendRawResponse(const TString& httpResourceId, TStringBuf rawResponse);
        THttpRequest SendStatusCode(const TString& httpResourceId, int statusCode);
        THttpRequest SendOkData(const TString& httpResourceId, TStringBuf data);
        THttpRequest SendOkJson(const TString& httpResourceId, const NJson::TJsonValue& json);

        void SetTsRunner(TScopedTasksSequenceRunnerBase* TSRunner) {
            TSRunner_ = TSRunner;
        }

        void AutoSendRepeatedlyOkData(const TString& httpResourceId, TString data);
        void ResetAutoSendingResource(const TString& httpResourceId);
        void ResetAutoSending();

    private:
        class TTestFetcher;
        void Fetch(const TString& httpResourceId, TTestFetcher* fetcher);
        void CancelFetch(const TString& httpResourceId, TTestFetcher* fetcher);

    private:
        TMap<TString, TTestFetcher*> ActiveFetchers_;
        TMutex Mutex_;
        TScopedTasksSequenceRunnerBase* TSRunner_ = nullptr;
        TMap<TString, TString> AutoResponses_;
    };

    using TTestHttpResourceResponder = TTestHttpResponder::TTestHttpResourceResponder;

} // namespace NMordaBlocks
