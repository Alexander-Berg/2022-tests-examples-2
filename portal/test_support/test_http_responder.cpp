#include "test_http_responder.h"

#include <portal/morda/blocks/core/net/http_fetcher.h>
#include <portal/morda/blocks/core/net/http_fetchers_factory.h>
#include <portal/morda/blocks/tasks_sequence/tasks_sequence.h>

#include <library/cpp/json/json_writer.h>

#include <util/datetime/base.h>
#include <util/system/guard.h>

#include <utility>

namespace NMordaBlocks {

    namespace {
        class THttpFetchersFactoryProtectAcc : public THttpFetchersFactory {
        public:
            using THttpFetchersFactory::SetFactoryForTests;
        };

    } // namespace

    class TTestHttpResponder::TTestFetcher : public IHttpFetcher {
    public:
        TTestFetcher(TTestHttpResponder* responder, TStringBuf httpResourceId)
            : Responder_(responder)
            , HttpResourceId_(httpResourceId) {
        }

        ~TTestFetcher() override {
            Responder_->CancelFetch(HttpResourceId_, this);
        }

        void Start() override {
            IsStarted_ = true;
        }

        void Fetch(const THttpRequest& request,
                   std::function<void(std::unique_ptr<THttpResponse>)> callback) override {
            Y_ASSERT(IsStarted_);
            TGuard lock(Mutex_);
            Requests_.push({request, TTasksSequence::Current(), std::move(callback)});
            if (Requests_.size() == 1)
                Responder_->Fetch(HttpResourceId_, this);
        }

        void SetWorkingTS(TIntrusivePtr<TTasksSequence> ts) override {
            Y_UNUSED(ts);
        }

        const TString& HttpResourceId() const override {
            return HttpResourceId_;
        }

        TIntrusivePtr<TTasksSequence> GetWorkingTS() const override {
            return nullptr;
        }

        const THttpRequest& Request() const {
            TGuard lock(Mutex_);
            return Requests_.front().Request_;
        }

        void SendResponse(std::unique_ptr<THttpResponse> response) {
            TRequestData data;
            {
                TGuard lock(Mutex_);
                data = Requests_.front();
                Requests_.pop();
                if (!Requests_.empty())
                    Responder_->Fetch(HttpResourceId_, this);
            }
            if (data.TasksSequence_.Get() == TTasksSequence::Current()) {
                std::move(data.Callback_)(std::move(response));
            } else {
                bool called = false;
                data.TasksSequence_->PostTask(
                    [ callback{std::move(data.Callback_)}, response{response.release()}, &called ]() {
                        std::move(callback)(std::unique_ptr<THttpResponse>(response));
                        called = true;
                    });
                while (!called) {
                    Sleep(TDuration::MicroSeconds(100));
                }
            }
        }

    private:
        TTestHttpResponder* Responder_;
        TString HttpResourceId_;
        bool IsStarted_ = false;
        struct TRequestData {
            THttpRequest Request_;
            TIntrusivePtr<TTasksSequence> TasksSequence_;
            std::function<void(std::unique_ptr<THttpResponse>)> Callback_;
        };
        TQueue<TRequestData> Requests_;
        TMutex Mutex_;
    };

    TTestHttpResponder::TTestHttpResourceResponder::TTestHttpResourceResponder(TTestHttpResponder* responder, const TString& httpResourceId)
        : Responder_(responder)
        , HttpResourceId_(httpResourceId) {
    }

    TTestHttpResponder::TTestHttpResourceResponder::~TTestHttpResourceResponder() = default;

    bool TTestHttpResponder::TTestHttpResourceResponder::IsHttpRequestStarted() const {
        return Responder_->IsHttpRequestStarted(HttpResourceId_);
    }

    void TTestHttpResponder::TTestHttpResourceResponder::WaitHttpRequest() const {
        return Responder_->WaitHttpRequest(HttpResourceId_);
    }

    const THttpRequest& TTestHttpResponder::TTestHttpResourceResponder::GetRequest() {
        return Responder_->GetRequest(HttpResourceId_);
    }

    THttpRequest TTestHttpResponder::TTestHttpResourceResponder::SendResponse(std::unique_ptr<THttpResponse> response) {
        return Responder_->SendResponse(HttpResourceId_, std::move(response));
    }

    THttpRequest TTestHttpResponder::TTestHttpResourceResponder::SendResponse(int statusCode, TStringBuf data, TVector<TString> additionalHeaders) {
        return Responder_->SendResponse(HttpResourceId_, statusCode, data, std::move(additionalHeaders));
    }

    THttpRequest TTestHttpResponder::TTestHttpResourceResponder::SendRawResponse(TStringBuf rawResponse) {
        return Responder_->SendRawResponse(HttpResourceId_, rawResponse);
    }

    THttpRequest TTestHttpResponder::TTestHttpResourceResponder::SendStatusCode(int statusCode) {
        return Responder_->SendStatusCode(HttpResourceId_, statusCode);
    }

    THttpRequest TTestHttpResponder::TTestHttpResourceResponder::SendOkData(TStringBuf data) {
        return Responder_->SendOkData(HttpResourceId_, data);
    }

    THttpRequest TTestHttpResponder::TTestHttpResourceResponder::SendOkJson(const NJson::TJsonValue& json) {
        return Responder_->SendOkJson(HttpResourceId_, json);
    }

    void TTestHttpResponder::TTestHttpResourceResponder::AutoSendRepeatedlyOkData(TString data) {
        return Responder_->AutoSendRepeatedlyOkData(HttpResourceId_, data);
    }

    void TTestHttpResponder::TTestHttpResourceResponder::ResetAutoSendingResource() {
        return Responder_->ResetAutoSendingResource(HttpResourceId_);
    }

    TTestHttpResponder::TTestHttpResponder() {
        THttpFetchersFactoryProtectAcc::SetFactoryForTests(
            [this](TStringBuf httpResourceId) -> std::unique_ptr<IHttpFetcher> {
                return std::make_unique<TTestFetcher>(this, httpResourceId);
            });
    }

    TTestHttpResponder::~TTestHttpResponder() {
        THttpFetchersFactoryProtectAcc::SetFactoryForTests(nullptr);
    }

    std::unique_ptr<TTestHttpResponder::TTestHttpResourceResponder> TTestHttpResponder::MakeResourceResponder(const TString& httpResourceId) {
        return std::make_unique<TTestHttpResourceResponder>(this, httpResourceId);
    }

    bool TTestHttpResponder::IsHttpRequestStarted(const TString& httpResourceId) const {
        TGuard lock(Mutex_);
        return ActiveFetchers_.find(httpResourceId) != ActiveFetchers_.end();
    }

    void TTestHttpResponder::WaitHttpRequest(const TString& httpResourceId) const {
        while (!IsHttpRequestStarted(httpResourceId)) {
            Sleep(TDuration::MicroSeconds(100));
        }
    }

    const THttpRequest& TTestHttpResponder::GetRequest(const TString& httpResourceId) {
        WaitHttpRequest(httpResourceId);
        TGuard lock(Mutex_);
        const auto it = ActiveFetchers_.find(httpResourceId);
        if (it == ActiveFetchers_.end())
            ythrow yexception() << "The fetching is not started.";

        return it->second->Request();
    }

    THttpRequest TTestHttpResponder::SendResponse(const TString& httpResourceId,
                                          std::unique_ptr<THttpResponse> response) {
        WaitHttpRequest(httpResourceId);
        TTestFetcher* fetcher = nullptr;
        {
            TGuard lock(Mutex_);
            auto it = ActiveFetchers_.find(httpResourceId);
            if (it == ActiveFetchers_.end())
                ythrow yexception() << "The fetching is not started.";

            fetcher = it->second;
            ActiveFetchers_.erase(it);
        }
        THttpRequest result = fetcher->Request();
        fetcher->SendResponse(std::move(response));
        if (TSRunner_ && TSRunner_->TasksSequence()->IsCurrent())
            TSRunner_->RunPendingTasks();

        return result;
    }

    THttpRequest TTestHttpResponder::SendRawResponse(const TString& httpResourceId,
                                             TStringBuf rawResponse) {
        auto response = std::make_unique<THttpResponse>();
        response->AppendData(TVector<char>(rawResponse.begin(), rawResponse.end()));
        if (!response->IsFinished())
            ythrow yexception() << "Invalid raw response.";

        return SendResponse(httpResourceId, std::move(response));
    }

    THttpRequest TTestHttpResponder::SendResponse(const TString& httpResourceId, int statusCode,
                                          TStringBuf data, TVector<TString> additionalHeaders) {
        TString rawResponse;
        rawResponse += "HTTP/1.1 " + ToString(statusCode) + " Test\n";
        rawResponse += "Content-Length:" + ToString(data.size()) + "\n";
        for (const auto& it : additionalHeaders) {
            rawResponse += it + "\n";
        }
        rawResponse += "\n";
        rawResponse += data;
        return SendRawResponse(httpResourceId, rawResponse);
    }

    THttpRequest TTestHttpResponder::SendStatusCode(const TString& httpResourceId, int statusCode) {
        return SendResponse(httpResourceId, statusCode, {}, {});
    }

    THttpRequest TTestHttpResponder::SendOkData(const TString& httpResourceId, TStringBuf data) {
        return SendResponse(httpResourceId, 200, data, {});
    }

    THttpRequest TTestHttpResponder::SendOkJson(const TString& httpResourceId,
                                        const NJson::TJsonValue& json) {
        return SendOkData(httpResourceId, WriteJson(json));
    }

    void TTestHttpResponder::Fetch(const TString& httpResourceId, TTestFetcher* fetcher) {
        TGuard lock(Mutex_);
        if (!ActiveFetchers_.emplace(httpResourceId, fetcher).second)
            ythrow yexception() << "The fetching already started.";

        const auto it = AutoResponses_.find(httpResourceId);
        if (it == AutoResponses_.end())
            return;

        TTasksSequence::Current()->PostTask(
            [ data{it->second}, httpResourceId, this ]() { SendOkData(httpResourceId, data); });
    }

    void TTestHttpResponder::CancelFetch(const TString& httpResourceId, TTestFetcher* fetcher) {
        Y_UNUSED(fetcher);
        TGuard lock(Mutex_);
        ActiveFetchers_.erase(httpResourceId);
    }

    void TTestHttpResponder::AutoSendRepeatedlyOkData(const TString& httpResourceId, TString data) {
        TGuard lock(Mutex_);
        AutoResponses_[httpResourceId] = std::move(data);
    }

    void TTestHttpResponder::ResetAutoSendingResource(const TString& httpResourceId) {
        TGuard lock(Mutex_);
        AutoResponses_.erase(httpResourceId);
    }

    void TTestHttpResponder::ResetAutoSending() {
        TGuard lock(Mutex_);
        AutoResponses_.clear();
    }

} // namespace NMordaBlocks
