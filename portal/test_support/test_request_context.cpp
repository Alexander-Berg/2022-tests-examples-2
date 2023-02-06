#include "test_request_context.h"

#include <portal/morda/blocks/contexts/request_context_fields.h>

#include <library/cpp/json/writer/json_value.h>

#include <util/datetime/base.h>

#include <utility>

namespace NMordaBlocks {

    TTestRequestContext::TTestRequestContext() {
        SetMordaZone(EMordaZone::Ru);
        SetLocale(ESupportedLocale::LANG_RUS);
        SetMordaRegion(REGION_MOSCOW);
        SetRegionByIP(REGION_MOSCOW);
        SetCrimeaStatus(ECrimeaStatus::IN_RU);
        SetMordaContent(EMordaContent::Big);
        SetIsYandexInternal(false);
        SetMordaContent(EMordaContent::Big);
        SetUserTimeZone("Europe/Moscow");
        SetUserLocalTime(NDatetime::TCivilSecond(2019, 01, 23, 17, 31, 15));
        SetUserIp("10.10.10.10");
        SetIsOldBrowserMode(false);
        GetTestMyCookie(); //Jsut init required field
    }

    TTestRequestContext::~TTestRequestContext() = default;

    ESupportedLocale TTestRequestContext::Locale() const {
        return Locale_;
    }

    EMordaZone TTestRequestContext::MordaZone() const {
        return MordaZone_;
    }

    ERegion TTestRequestContext::MordaRegion() const {
        return MordaRegion_;
    }

    ERegion TTestRequestContext::RegionByIP() const {
        return RegionByIP_;
    }

    ERegion TTestRequestContext::HomeRegion() const {
        return HomeRegion_;
    }

    ERegion TTestRequestContext::WorkRegion() const {
        return WorkRegion_;
    }

    ECrimeaStatus TTestRequestContext::CrimeaStatus() const {
        return CrimeaStatus_;
    }

    EMordaContent TTestRequestContext::MordaContent() const {
        return MordaContent_;
    }

    bool TTestRequestContext::IsYandexInternal() const {
        return Proto_.is_yandex_internal();
    }

    TInstant TTestRequestContext::UserTimeStamp() const {
        return TInstant::Seconds(Proto_.user_time_stamp());
    }

    const NDatetime::TTimeZone& TTestRequestContext::UserTimeZone() const {
        return UserTimeZone_;
    }

    void TTestRequestContext::SetUserTimeZone(TStringBuf value) {
        SetUserTimeZone(NDatetime::GetTimeZone(value));
    }

    void TTestRequestContext::SetUserLocalTime(const NDatetime::TCivilSecond& localTime) {
        SetUserTimeStamp(NDatetime::Convert(localTime, UserTimeZone()));
    }

    void TTestRequestContext::SetUserLocalTime(TStringBuf strTime) {
        SetUserLocalTime(
            NDatetime::Convert(TInstant::ParseIso8601(strTime), NDatetime::TTimeZone()));
    }

    const TGeoLocation& TTestRequestContext::GeoLocation() const {
        return GeoLocation_;
    }

    const THashSet<TString>& TTestRequestContext::PromoGroups() const {
        return PromoGroups_;
    }

    const TString& TTestRequestContext::RequestId() const {
        return RequestId_;
    }

    const TString& TTestRequestContext::L7RequestId() const {
        return Proto_.l7_request_id();
    }

    EMordaApi TTestRequestContext::Api() const {
        return Api_;
    }

    EApiVersion TTestRequestContext::ApiVersion() const {
        return ApiVersion_;
    }

    EVpsVersion TTestRequestContext::VpsVersion() const {
        return VpsVersion_;
    }

    EMordaApiClient TTestRequestContext::ApiClient() const {
        return ApiClient_;
    }

    EMordaSize TTestRequestContext::MordaSize() const {
        return MordaSize_;
    }

    bool TTestRequestContext::IsDesktopNotificationsOn() const {
        return IsDesktopNotificationsOn_;
    }

    const TString* TTestRequestContext::GetHttpHeaderByName(TStringBuf name) const {
        const auto it = Proto_.http_headers().find(to_lower(TString(name)));
        if (it == Proto_.http_headers().end())
            return nullptr;

        return &(it->second);
    }

    const TString* TTestRequestContext::GetCookieValueByName(TStringBuf name) const {
        TString nameLower(name);
        nameLower.to_lower();
        const auto it = Cookies_.find(nameLower);
        if (it == Cookies_.end())
            return nullptr;

        return &(it->second.Value);
    }

    const TString* TTestRequestContext::GetYCookieValue(TStringBuf name) const {
        const auto it = Proto_.y_cookies().find(to_lower(TString(name)));
        if (it == Proto_.y_cookies().end())
            return nullptr;

        return &(it->second);
    }

    const TString* TTestRequestContext::GetCgiStringParam(ECgiParam name) const {
        const auto& it = Proto_.cgi_params().find(ToString(name));
        if (it == Proto_.cgi_params().end())
            return nullptr;

        return &(it->second);
    }

    const TString& TTestRequestContext::YandexUserID() const {
        return Proto_.yandex_uid();
    }

    const TString& TTestRequestContext::Clid() const {
        return Proto_.clid();
    }

    const TString& TTestRequestContext::Domain() const {
        return Domain_;
    }

    const TString& TTestRequestContext::UserIp() const {
        return Proto_.user_ip();
    }

        // experiments:
    TMaybe<TRequestContext::EExperimentValues> TTestRequestContext::GetExperimentValue(const TString& expName) const {
        const auto it = ExperimentValues_.find(expName);
        if (it == ExperimentValues_.end())
            return {};

        return it->second;
    }

    bool TTestRequestContext::GetBoolABFlag(TStringBuf flagName) const {
        const NJson::TJsonValue* value = GetABFlagValue(flagName);
        return value ? value->GetBooleanRobust() : false;
    }

    TMaybe<TString> TTestRequestContext::GetStringABFlag(TStringBuf flagName) const {
         const NJson::TJsonValue* value = GetABFlagValue(flagName);
        if (!value)
            return {};

        return value->GetStringRobust();
    }

    TMaybe<long long> TTestRequestContext::GetIntABFlag(TStringBuf flagName) const {
          const NJson::TJsonValue* value = GetABFlagValue(flagName);
        if (!value)
            return {};

        return value->GetIntegerRobust();
    }

    TMaybe<unsigned long long> TTestRequestContext::GetUIntABFlag(TStringBuf flagName) const {
        const NJson::TJsonValue* value = GetABFlagValue(flagName);
        if (!value)
            return {};

        return value->GetUIntegerRobust();
    }

    const NJson::TJsonValue* TTestRequestContext::GetABFlagValue(TStringBuf flagName) const {
        if (!ABFlags_.IsMap())
            return nullptr;

        const NJson::TJsonValue* result;
        if (!ABFlags_.GetValuePointer(flagName, &result))
            return nullptr;

        return result;
    }

    // Garbage:
    bool TTestRequestContext::IsAddWidgetMode() const {
        return IsAddWidgetMode_;
    }

    bool TTestRequestContext::IsApiYabrowser2Vertical() const {
        return IsApiYabrowser2Vertical_;
    }

    bool TTestRequestContext::IsVpsIosFormat() const {
        return IsVpsIosFormat_;
    }

    const THashSet<TString>& TTestRequestContext::GetAllowedBKFlags() const {
        return AllowedBKFlags_;
    }

    bool TTestRequestContext::IsOldBrowserMode() const {
        return Proto_.is_old_browser_mode();
    }

    TRequestContextProto& TTestRequestContext::Proto() {
        return Proto_;
    }

    void TTestRequestContext::AddYCookie(TStringBuf name, TStringBuf value) {
        (*(Proto_.mutable_y_cookies()))[to_lower(TString(name))] = TString(value);
    }

    void TTestRequestContext::DropYCookies() {
        Proto_.clear_y_cookies();
    }

    void TTestRequestContext::SetGeoLocation(double lat, double lon) {
        TGeoLocation newLocation;
        newLocation.SetGeoPoint(TGeoPoint(lat, lon));
        SetGeoLocation(std::move(newLocation));
    }

    void TTestRequestContext::ResetGeoLocation() {
        SetGeoLocation(TGeoLocation());
    }

    void TTestRequestContext::SetCookie(TCookie cookie) {
        TString nameLower = cookie.Name;
        nameLower.to_lower();
        Y_ASSERT(!nameLower.empty());
        Cookies_[nameLower] = std::move(cookie);
    }

    void TTestRequestContext::SetCookie(TStringBuf name, TString value) {
        TCookie cookie;
        cookie.Name = name;
        cookie.Value = std::move(value);
        SetCookie(std::move(cookie));
    }

    void TTestRequestContext::AddCgiParam(TStringBuf name, TString value) {
        AddCgiParam(FromString<ECgiParam>(name), std::move(value));
    }

    void TTestRequestContext::AddCgiParam(ECgiParam name, TString value) {
        (*Proto_.mutable_cgi_params())[ToString(name)] = value;
    }

    void TTestRequestContext::EnableExperiment(TStringBuf expName) {
        ExperimentValues_[expName] = EExperimentValues::Enabled;
    }

    void TTestRequestContext::DisableExperiment(TStringBuf expName) {
        ExperimentValues_.erase(expName);
    }

    void TTestRequestContext::SetExperimentIsEthalon(TStringBuf expName) {
        ExperimentValues_[expName] = EExperimentValues::Ethalon;
    }

    void TTestRequestContext::SetABFlagValue(TStringBuf flagName, const NJson::TJsonValue& value) {
        ABFlags_[flagName] = value;
    }

    void TTestRequestContext::AddAllowedBKFlag(TStringBuf bkFlag) {
        AllowedBKFlags_.emplace(bkFlag);
    }

    TRequestContextProto TTestRequestContext::MakeProto() const {
        TRequestContextProto result = Proto_;
        *(result.mutable_user_agent()) = UserAgent().ToUserAgentProto();

        for (const auto& it : Cookies_) {
            (*result.mutable_cookies())[to_lower(it.first)].set_value(it.second.Value);
        }

        Y_ENSURE(result.IsInitialized(), TString("Not all required fields was filled: ") + result.InitializationErrorString());
        return result;
    }

    NJson::TJsonValue TTestRequestContext::MakeLegacyJson() const {
        NJson::TJsonValue result;
        result[API_NAME] = ToString(Api());
        result[API_VERSION] = ToString(ApiVersion());
        result[API_CLIENT] = ToString(ApiClient());
        result[LOCALE] = LocaleToString(Locale());
        result[MORDA_CONTENT] = ToString(MordaContent());
        result[MORDA_ZONE] = ToString(MordaZone());
        result[GEO_BY_DOMAIN_IP] = static_cast<ui32>(MordaRegion());
        result[REGION_BY_IP] = static_cast<ui32>(RegionByIP());
        result[HOME_REGION] = static_cast<ui32>(HomeRegion());
        result[WORK_REGION] = static_cast<ui32>(WorkRegion());
        result[REQUEST_ID] = RequestId();

        if (GeoLocation().GetGeoPoint()) {
            NJson::TJsonValue& geoDetection = result[GEO_DETECTION];
            geoDetection["lat"] = GeoLocation().GetGeoPoint().Lat();
            geoDetection["lon"] = GeoLocation().GetGeoPoint().Lon();
            if (GeoLocation().GetExactGeoPoint()) {
                NJson::TJsonValue& gpauto = geoDetection["gpauto"];
                gpauto["lat"] = GeoLocation().GetExactGeoPoint().Lat();
                gpauto["lon"] = GeoLocation().GetExactGeoPoint().Lon();
                gpauto["ok"] = 1;
                gpauto["acc"] = 1;
                gpauto["age"] = 1;
            }
        }
        switch (MordaSize()) {
            case EMordaSize::Normal:
                result[MORDA_SIZE] = "big";
                break;
            case EMordaSize::Small:
                result[MORDA_SIZE] = "touch";
                break;
            case EMordaSize::Tiny:
                result[MORDA_SIZE] = "tel";
                break;
            case EMordaSize::Unknown:
                break;
        }

        for (const auto& it : PromoGroups_) {
            result[TARGETING_INFO]["promo-groups"].AppendValue(it);
        }
        result[EDIT_MODE] = EditMode();
        result[NO_PROMO] = NoPromo();
        NJson::TJsonValue& authInfo = result[AUTH_INFO];
        authInfo["uid"] = AuthInfo().UID();
        authInfo["login"] = AuthInfo().Login();
        authInfo["plus_status"] = AuthInfo().PlusStatus();
        result[DOMAIN_FIELD] = Domain();
        for (const auto& it : ExperimentValues_) {
            result[EXPERIMENTS_SUB_SECTION_NAME][it.first] = static_cast<int>(it.second);
        }
        // result[AB_FLAGS_SUB_SECTION_NAME] = //TODO
        result[GARBAGE_SUB_SECTION_NAME][ADD_MODE] = IsAddWidgetMode();
        result[GARBAGE_SUB_SECTION_NAME][IS_API_YABROWSER_2_VERTICAL] = IsApiYabrowser2Vertical();
        result[GARBAGE_SUB_SECTION_NAME][IS_VPS_IOS_FORMAT] = IsVpsIosFormat();

        for (const auto& it : AllowedBKFlags_) {
            result[BK_FLAGS_SUBSECTION_NAME].AppendValue(it);
        }
        return result;
    }

    void TTestRequestContext::SetHeader(const TString& name, TString value) {
        (*Proto_.mutable_http_headers())[to_lower(name)] = value;
    }

} // namespace NMordaBlocks
