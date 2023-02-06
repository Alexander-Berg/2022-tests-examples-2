#pragma once

#include <portal/morda/blocks/request_context/request_context.h>

#include <portal/morda/blocks/request_context/request_context.pb.h>
#include <portal/morda/blocks/types/geo_location.h>

#include <library/cpp/http/client/cookies/cookie.h>
#include <library/cpp/json/writer/json_value.h>

#include <memory>

namespace NMordaBlocks {

    //  Default values:
    //  Locale : ESupportedLocale::LANG_RUS
    //  MordaZone : EMordaZone::Ru
    //  MordaRegion : REGION_MOSCOW
    //  CrimeaStatus : ECrimeaStatus::IN_RU
    //  MordaContent : EMordaContent::Big
    //  IsYandexInternal : false
    //  TimeZone : "Europe/Moscow"
    //  UserLocalTime : 2019-01-23 17:31:15 (Taking into account the time zone)
    class TTestRequestContext : public TRequestContext {
    public:
        using TCookie = NHttp::TCookie;

        TTestRequestContext();

        ~TTestRequestContext() override;

        ESupportedLocale Locale() const override;

        EMordaZone MordaZone() const override;
        ERegion MordaRegion() const override;
        ERegion RegionByIP() const override;
        ERegion HomeRegion() const override;
        ERegion WorkRegion() const override;
        ECrimeaStatus CrimeaStatus() const override;
        EMordaContent MordaContent() const override;
        bool IsYandexInternal() const override;

        TInstant UserTimeStamp() const override;
        const NDatetime::TTimeZone& UserTimeZone() const override;

        const TGeoLocation& GeoLocation() const override;
        const THashSet<TString>& PromoGroups() const override;

        const TString& RequestId() const override;
        const TString& L7RequestId() const override;

        EMordaApi Api() const override;
        EApiVersion ApiVersion() const override;
        EVpsVersion VpsVersion() const override;
        EMordaApiClient ApiClient() const override;

        EMordaSize MordaSize() const override;
        bool IsDesktopNotificationsOn() const override;

        const TString* GetHttpHeaderByName(TStringBuf name) const override;
        const TString* GetCookieValueByName(TStringBuf name) const override;
        const TString* GetYCookieValue(TStringBuf name) const override;
        const TString* GetCgiStringParam(ECgiParam name) const override;

        const TString& YandexUserID() const override;
        const TString& Clid() const override;

        const TString& GetProxyHost() const override {
            return Proto_.proxy_host();
        }

        const TUserAgent& UserAgent() const override {
            return TestUserAgent_;
        }

        const TAuthInfo& AuthInfo() const override {
            return AuthInfo_;
        }

        const TString& Domain() const override;

        const TString& UserIp() const override;

           // experiments:
        TMaybe<EExperimentValues> GetExperimentValue(const TString& expName) const override;
        bool GetBoolABFlag(TStringBuf flagName) const override;
        TMaybe<TString> GetStringABFlag(TStringBuf flagName) const override;
        TMaybe<long long> GetIntABFlag(TStringBuf flagName) const override;
        TMaybe<unsigned long long> GetUIntABFlag(TStringBuf flagName) const override;

        // Garbage:
        bool IsAddWidgetMode() const override;
        bool IsApiYabrowser2Vertical() const override;
        bool IsVpsIosFormat() const override;

        // BK Flags
        const THashSet<TString>& GetAllowedBKFlags() const override;

        bool IsOldBrowserMode() const override;

        TRequestContextProto& Proto() override;

        void SetLocale(ESupportedLocale value) {
            Locale_ = value;
        }

        void SetMordaZone(EMordaZone value) {
            MordaZone_ = value;
        }

        void SetMordaRegion(ERegion region) {
            MordaRegion_ = region;
        }

        void SetMordaRegionInt(int region) {
            SetMordaRegion(static_cast<ERegion>(region));
        }

        void SetRegionByIP(ERegion region) {
            RegionByIP_ = region;
        }

        void SetHomeRegion(ERegion region) {
            HomeRegion_ = region;
        }

        void SetWorkRegion(ERegion region) {
            WorkRegion_ = region;
        }

        void SetRegionByIPInt(int region) {
            SetRegionByIP(static_cast<ERegion>(region));
        }

        void SetCrimeaStatus(ECrimeaStatus value) {
            CrimeaStatus_ = value;
        }

        void SetMordaContent(EMordaContent value) {
            MordaContent_ = value;
        }

        void SetIsYandexInternal(bool value) {
            Proto_.set_is_yandex_internal(value);
        }

        void SetUserTimeStamp(const TInstant& value) {
            Proto_.set_user_time_stamp(value.TimeT());
        }

        void SetUserTimeZone(const NDatetime::TTimeZone& value) {
            UserTimeZone_ = value;
        }

        void SetUserTimeZone(TStringBuf value);

        void SetUserLocalTime(const NDatetime::TCivilSecond& localTime);
        void SetUserLocalTime(TStringBuf strTime);

        TGeoLocation& GetTestGeoLocation() {
            return GeoLocation_;
        }

        void AddYCookie(TStringBuf name, TStringBuf value);
        void DropYCookies();

        THashSet<TString>& GetTestPromoGroups() {
            return PromoGroups_;
        }

        void SetRequestId(const TString& value) {
            RequestId_ = value;
        }

        void SetL7RequestId(const TString& value) {
            Proto_.set_l7_request_id(std::move(value));
        }

        void SetApi(EMordaApi value) {
            Api_ = value;
        }

        void SetApiVersion(EApiVersion value) {
            ApiVersion_ = value;
        }

        void SetVpsVersion(EVpsVersion value) {
            VpsVersion_ = value;
        }

        void SetApiClient(EMordaApiClient value) {
            ApiClient_ = value;
        }

        void SetMordaSize(EMordaSize value) {
            MordaSize_ = value;
        }

        void SetIsDesktopNotificationsOn(bool value) {
            IsDesktopNotificationsOn_ = value;
        }

        void SetUserID(TString value) {
            AuthInfo_.SetUID(std::move(value));
        }

        void SetYandexUserID(TString value) {
            Proto_.set_yandex_uid(std::move(value));
        }

        void SetGeoLocation(TGeoLocation geoLocation) {
            GeoLocation_ = std::move(geoLocation);
        }
        void SetGeoLocation(double lat, double lon);
        void ResetGeoLocation();

        void SetProxyHost(TString host) {
            Proto_.set_proxy_host(std::move(host));
        }

        bool EditMode() const override {
            return false;
        }

        bool NoPromo() const override {
            return false;
        }

        TUserAgent& GetTestUserAgent() {
            return TestUserAgent_;
        }

        void SetCookie(TCookie cookie);
        void SetCookie(TStringBuf name, TString value);

        void AddCgiParam(TStringBuf name, TString value);
        void AddCgiParam(ECgiParam name, TString value);

        void SetClid(TString clid) {
            Proto_.set_clid(std::move(clid));
        }

        TAuthInfo& GetTestAuthInfo() {
            return AuthInfo_;
        }

        void SetDomain(TString domain) {
            Domain_ = std::move(domain);
        }

        void SetUserIp(TString ip) {
            Proto_.set_user_ip(std::move(ip));
        }

        void EnableExperiment(TStringBuf expName);
        void DisableExperiment(TStringBuf expName);
        void SetExperimentIsEthalon(TStringBuf expName);

        void SetABFlagValue(TStringBuf flagName, const NJson::TJsonValue& value);

        void SetIsAddWidgetMode(bool value) {
            IsAddWidgetMode_ = value;
        }

        void SetIsApiYabrowser2Vertical(bool value) {
            IsApiYabrowser2Vertical_ = value;
        }

        void SetIsVpsIosFormat(bool value) {
            IsVpsIosFormat_ = value;
        }

        void AddAllowedBKFlag(TStringBuf bkFlag);

        TRequestContextProto MakeProto() const;
        NJson::TJsonValue MakeLegacyJson() const;

        void SetIsOldBrowserMode(bool value) {
            Proto_.set_is_old_browser_mode(value);
        }

        TMyCookieProto* GetTestMyCookie() {
            return Proto_.mutable_my_cookie();
        }

        void SetHeader(const TString& name, TString value);

    private:
        const NJson::TJsonValue* GetABFlagValue(TStringBuf flagName) const;

    private:
        TRequestContextProto Proto_;

        ESupportedLocale Locale_;
        EMordaZone MordaZone_;

        ERegion MordaRegion_;
        ERegion RegionByIP_;
        ERegion HomeRegion_;
        ERegion WorkRegion_;
        ECrimeaStatus CrimeaStatus_;
        EMordaContent MordaContent_;

        NDatetime::TTimeZone UserTimeZone_;
        TGeoLocation GeoLocation_;
        THashSet<TString> PromoGroups_;

        TString RequestId_;

        EMordaApi Api_ = EMordaApi::None;
        EApiVersion ApiVersion_ = EApiVersion::None;
        EVpsVersion VpsVersion_ = EVpsVersion::None;
        EMordaApiClient ApiClient_ = EMordaApiClient::Generic;

        EMordaSize MordaSize_ = EMordaSize::Unknown;
        bool IsDesktopNotificationsOn_ = false;

        TUserAgent TestUserAgent_;
        THashMap<TString, TCookie> Cookies_;

        TAuthInfo AuthInfo_;
        TString Domain_;

        // Experiments:
        NJson::TJsonValue ABFlags_;
        THashMap<TString, EExperimentValues> ExperimentValues_;

        // Garbage:
        bool IsAddWidgetMode_ = false;
        bool IsApiYabrowser2Vertical_ = false;
        bool IsVpsIosFormat_ = false;

        // BK Flags:
        THashSet<TString> AllowedBKFlags_;
    };

} // namespace NMordaBlocks
