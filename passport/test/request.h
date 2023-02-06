#pragma once

#include <passport/infra/libs/cpp/request/request.h>

#include <map>

namespace NPassport::NTest {
    class TRequest: public NCommon::TRequest {
    public:
        static const TString EMPTY_;
        static const NCommon::TExtendedArg EMPTY_ARG_;

        TString Path = "/blackbox";
        TString Method = "GET";

        TString RequestBody;
        TString RequestCgi;

        TString Host;

        TString RemoteAddr;
        NCommon::THttpHeaders InHeaders;
        std::map<TString, NCommon::TExtendedArg> Args;

        std::map<TString, TString> OutHeaders;
        std::map<TString, NPassport::NCommon::TCookie> Cookies;

        TString Response;
        HttpCodes Status = HTTP_OK;

        bool HasHeader(const TString& h) const override {
            return InHeaders.find(h) != InHeaders.end();
        }

        const TString& GetHeader(const TString& h) const override {
            auto it = InHeaders.find(h);
            return it == InHeaders.end() ? EMPTY_ : it->second;
        }

        NCommon::THttpHeaders GetAllHeaders() const override {
            return InHeaders;
        }

        bool HasCookie(const TString&) const override {
            return true;
        }

        const TString& GetCookie(const TString& cookie) const override {
            auto it = Cookies.find(cookie);
            return it == Cookies.end() ? EMPTY_ : it->second.Value();
        }

        bool HasArg(const TString& arg) const override {
            return Args.find(arg) != Args.end();
        }

        const TString& GetArg(const TString& arg) const override {
            auto it = Args.find(arg);
            if (it != Args.end()) {
                return it->second.Value;
            }
            return EMPTY_;
        }

        const NCommon::TExtendedArg& GetExtendedArg(const TString& name) const override {
            auto it = Args.find(name);
            return it == Args.end() ? EMPTY_ARG_ : it->second;
        }

        const TString& GetRemoteAddr() const override {
            return RemoteAddr;
        }

        TString GetUri() const override {
            return EMPTY_;
        }

        const TString& GetRequestId() const override {
            return EMPTY_;
        }

        const TString& GetPath() const override {
            return Path;
        }

        void ArgNames(std::vector<TString>&) const override {
        }

        void SetStatus(HttpCodes status) override {
            Status = status;
        }

        void SetHeader(const TString& key, const TString& value) override {
            OutHeaders[key] = value;
        }

        void Write(const TString& s) override {
            Response.append(s);
        }

        bool IsSecure() const override {
            return true;
        }

        const TString& GetQueryString() const override {
            return EMPTY_;
        }

        const TString& GetRequestMethod() const override {
            return Method;
        }

        const TString& GetHost() const override {
            return Host;
        }

        bool IsBodyEmpty() const override {
            return false;
        }

        void SetCookie(const NPassport::NCommon::TCookie& cookie) override {
            Cookies.insert_or_assign(cookie.Name(), cookie);
        }

        HttpCodes GetStatusCode() const override {
            return Status;
        }

        size_t GetResponseSize() const override {
            return 0;
        }

        const TString& GetRequestBody() const override {
            return RequestBody;
        }

        TStringBuf GetRequestCgi() const override {
            return RequestCgi;
        }

        void ScanCgiFromBody() override {
        }

        void ForceProvideRequestId() override {
        }

        TDuplicatedArgs GetDuplicatedArgs() const override {
            return {};
        }

        NCommon::TCookie& GetOutCookie(const TString& name) {
            auto it = Cookies.find(name);
            if (it == Cookies.end()) {
                throw yexception() << "No cookie with name " << name;
            }
            return it->second;
        }
    };
}
