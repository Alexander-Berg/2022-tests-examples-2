#include "fuzz_block_runner.h"

#include <portal/morda/blocks/common/block_base.h>
#include <portal/morda/blocks/contexts/request_context_fields.h>
#include <portal/morda/blocks/contexts/request_context_impl.h>
#include <portal/morda/blocks/test_support/fuzz_helpers.h>
#include <portal/morda/blocks/types/context_types.h>
#include <apphost/lib/service_testing/service_testing.h>

#include <library/cpp/json/json_value.h>
#include <library/cpp/testing/unittest/gtest.h>

#include <util/generic/serialized_enum.h>
#include <util/generic/string.h>
#include <util/random/mersenne.h>

#include <utility>
#include <type_traits>


using NAppHost::NService::TTestContext;

namespace NMordaBlocks {

    namespace {

        using TRandGenerator = TMersenne<ui64>;

        template <typename T>
        const TVector<T>& ExtreamValues() {
            static TVector<T> svalues;
            if (svalues.empty()) {
                svalues.push_back(std::numeric_limits<T>::min());
                svalues.push_back(std::numeric_limits<T>::max());
                if (std::is_signed<T>::value) {
                    svalues.push_back(static_cast<T>(0));
                    svalues.push_back(static_cast<T>(-1));
                    svalues.push_back(static_cast<T>(-100));
                }
                svalues.push_back(static_cast<T>(1));
                svalues.push_back(static_cast<T>(100));
                if (std::is_floating_point<T>::value) {
                    svalues.push_back(static_cast<T>(-10.6));
                    svalues.push_back(static_cast<T>(12.5));
                }
            }
            return svalues;
        }

        template <>
        const TVector<bool>& ExtreamValues<bool>() {
            static TVector<bool> svalues(true, false);
            return svalues;
        }

        template <>
        const TVector<TString>& ExtreamValues<TString>() {
            static TVector<TString> svalues;
            if (svalues.empty()) {
                svalues.push_back("");
                svalues.push_back(" ");
                svalues.push_back("         ");
                svalues.push_back("\n");
                svalues.push_back("\r");
                svalues.push_back("0");
                svalues.push_back("1");
                svalues.push_back("true");
                svalues.push_back("false");
                svalues.push_back("yes");
                svalues.push_back("no");
                svalues.push_back("null");
                svalues.push_back("undef");
                svalues.push_back(".");
                svalues.push_back(",");
                svalues.push_back("a,b,c,d,e");
                svalues.push_back("a.b.c.d.e");
                svalues.push_back("не аски");
                svalues.push_back("any string");
                svalues.push_back("100500");
                svalues.push_back("10050000000000000000000000000000");
                svalues.push_back("-100500");
                svalues.push_back("-1005000000000000000000000000000");
                svalues.push_back("100.5.00");
                svalues.push_back("1.5");
                svalues.push_back("-2.4");
                svalues.push_back("100.5.-00");
                svalues.push_back("\xc3\x28");
                svalues.push_back("\xa0\xa1");
                svalues.push_back("\xe2\x28\xa1");
                svalues.push_back("\xe2\x82\x28");
                svalues.push_back("\xf0\x28\x8c\xbc");
                svalues.push_back("\xf0\x28\x8c\x28");
                svalues.push_back(ToString(std::numeric_limits<int>::min()));
                svalues.push_back(ToString(std::numeric_limits<int>::max()));
                svalues.push_back(ToString(std::numeric_limits<long long>::max()));
                svalues.push_back(ToString(std::numeric_limits<long long>::min()));
                svalues.push_back(ToString(std::numeric_limits<unsigned long long>::max()) + "0");
                svalues.push_back(ToString(std::numeric_limits<long long>::min()) + "0");
                svalues.push_back(ToString(std::numeric_limits<double>::max()));
                svalues.push_back(ToString(std::numeric_limits<double>::min()));
                svalues.push_back(ToString(std::numeric_limits<double>::max()) + "0");
                svalues.push_back(ToString(std::numeric_limits<double>::min()) + "0");
            }
            return svalues;
        }

        template <>
        const TVector<TNumberedVersion>& ExtreamValues<TNumberedVersion>() {
             static TVector<TNumberedVersion> svalues;
            if (svalues.empty()) {
                svalues.push_back(TNumberedVersion());
                svalues.push_back(TNumberedVersion("1.0"));
                svalues.push_back(TNumberedVersion("2.3"));
                svalues.push_back(TNumberedVersion("5.1"));
                svalues.push_back(TNumberedVersion("8"));
                svalues.push_back(TNumberedVersion("10.3"));
                svalues.push_back(TNumberedVersion("20"));
                svalues.push_back(TNumberedVersion("20.7"));
                svalues.push_back(TNumberedVersion("100.500"));
                svalues.push_back(TNumberedVersion("100500.100500.100500.100500.100500.100500"));
            }
            return svalues;
        }

        template <typename T>
        T ReadValue(TRandGenerator& randIn) {
            const ui64 rand = randIn.GenRand64();
            T result;
            memcpy(&result, &rand, sizeof(result));
            return result;
        }

        template <typename T>
        T GetRandValueT(TRandGenerator& randIn, TVector<T> values) {
            size_t index = ReadValue<size_t>(randIn) % (values.size() + 1);
            if (index == values.size()) {
                index = ReadValue<size_t>(randIn) % ExtreamValues<T>().size();
                return ExtreamValues<T>()[index];
            }
            return values[index];
        }

        template <typename T>
        TMaybe<T> GetRandMaybeValueT(TRandGenerator& randIn, TVector<T> values) {
            size_t index = ReadValue<size_t>(randIn) % (values.size() + 2);
            if (index == values.size()) {
                index = ReadValue<size_t>(randIn) % ExtreamValues<T>().size();
                return ExtreamValues<T>()[index];
            }
            if (index == values.size() + 1) {
                return {};
            }
            return values[index];
        }

        template <typename T>
        TVector<TString> GetEnumStringValues() {
            TVector<TString> result;
            for (const auto it : GetEnumAllValues<T>()) {
                result.push_back(ToString(it));
            }
            return result;
        }

        template <typename T>
        TVector<size_t> GetEnumIntValues() {
            TVector<size_t> result;
            for (const auto it : GetEnumAllValues<T>()) {
                result.push_back(static_cast<size_t>(it));
            }
            return result;
        }

        template <>
        TVector<TString> GetEnumStringValues<EOSFamily>() {
            static const TVector<TString> result = {
                "unknown",
                "windows",
                "android",
                "ios",
                "linux",
                "macos",
                "java",
                "windowsphone",
                "windowsrt",
                "symbian",
                "windowsmobile",
                "tizen",
                "chromeos",
                "series40",
                "freebsd",
                "bada",
                "blackberry",
                "sunos",
                "rimtabletos",
                "meego",
                "nucleus",
                "webos",
                "openbsd",
                "os/2",
                "firefoxos",
                "netbsd",
                "unknownnix",
                "unix",
                "brew",
                "qnx",
                "moblin",
                "aix",
                "irix",
                "hp-ux",
                "palmos"};
            return result;
        }

        template <>
        TVector<size_t> GetEnumIntValues<EOSFamily>() {
            TVector<size_t> result;
            for (const auto& it : GetEnumStringValues<EOSFamily>()) {
                result.push_back(static_cast<size_t>(FromString<EOSFamily>(it)));
            }
            return result;
        }

        template <typename T>
        TString GetRandEnumStringValue(TRandGenerator& randIn) {
            return GetRandValueT<TString>(randIn, GetEnumStringValues<T>());
        }

        template <typename T>
        TMaybe<TString> GetRandMayBeEnumStringValue(TRandGenerator& randIn) {
            return GetRandMaybeValueT<TString>(randIn, GetEnumStringValues<T>());
        }

        template <typename T>
        size_t GetRandEnumIntValue(TRandGenerator& randIn) {
            return GetRandValueT<size_t>(randIn, GetEnumIntValues<T>());
        }

        template <typename T>
        TMaybe<size_t> GetRandMayBeEnumIntValue(TRandGenerator& randIn) {
            return GetRandMaybeValueT<size_t>(randIn, GetEnumIntValues<T>());
        }

        constexpr auto REGION_WITH_TRAFFIC = static_cast<ERegion>(12345);
        constexpr auto MAX_REGION = static_cast<ERegion>(250);
        constexpr auto DEFAULT_MORDA_ZONE = "ru";
        const THashSet<TString> LOCALES{
            "be", "en", "id", "kk", "ru", "tr",
            "tt", "uk", "uz", "zh-Hans", "klingon", "не аски"
        };

        NJson::TJsonValue CreateRequestLegacyPart(TMemoryInput& randIn) {
            NJson::TJsonValue result;
            TrySetValue(&result, MORDA_ZONE, GetMordaZoneJsonValue(randIn, DEFAULT_MORDA_ZONE));
            TrySetValue(&result, LOCALE, GetLocaleJsonValue(randIn, LOCALES, "ru"));
            TrySetValue(&result, AUTH_INFO, GetAuthInfoJsonValue(randIn));
            TrySetValue(&result, GEO_DETECTION, GetGeoLocationJsonValue(randIn));
            TrySetValue(&result, TARGETING_INFO, GetTargetingInfoJsonValue(randIn));
            TrySetValue(&result, GEO_BY_DOMAIN_IP, GetRegionJsonValue(randIn, REGION_WITH_TRAFFIC, MAX_REGION));
            TrySetValue(&result, REGION_BY_IP, GetRegionJsonValue(randIn, REGION_WITH_TRAFFIC, MAX_REGION));
            TrySetValue(&result, HOME_REGION, GetRegionJsonValue(randIn, REGION_WITH_TRAFFIC, MAX_REGION));
            TrySetValue(&result, WORK_REGION, GetRegionJsonValue(randIn, REGION_WITH_TRAFFIC, MAX_REGION));

            TrySetValue(&result, API_VERSION, GetEnumJsonValue<EApiVersion>(randIn));
            TrySetValue(&result, API_CLIENT, GetEnumJsonValue<EMordaApiClient>(randIn));
            TrySetValue(&result, MORDA_CONTENT, GetEnumJsonValue<EMordaContent>(randIn));
            TrySetValue(&result, MORDA_SIZE, GetEnumJsonValue<EMordaContent>(randIn));

            TrySetValue(&result, REQUEST_ID, GetStringJsonValue(randIn));

            TrySetValue(&result, EDIT_MODE, GetBooleanJsonValue(randIn));
            TrySetValue(&result, NO_PROMO, GetBooleanJsonValue(randIn));

            // Garbage:
            TrySetValue(&result[GARBAGE_SUB_SECTION_NAME], ADD_MODE, GetBooleanJsonValue(randIn));
            TrySetValue(&result[GARBAGE_SUB_SECTION_NAME], IS_API_YABROWSER_2_VERTICAL, GetBooleanJsonValue(randIn));
            TrySetValue(&result[GARBAGE_SUB_SECTION_NAME], IS_VPS_IOS_FORMAT, GetBooleanJsonValue(randIn));

            // Experiments:
            TrySetValue(&result, EXPERIMENTS_SUB_SECTION_NAME, GetMapJsonValue(randIn));
            TrySetValue(&result,AB_FLAGS_SUB_SECTION_NAME, GetMapJsonValue(randIn));
            // Bk flags:
            TrySetValue(&result, BK_FLAGS_SUBSECTION_NAME, GetArrayJsonValue(randIn));
            return result;
        }

        TRequestContextProto CreateRequestPart(TRandGenerator& randIn) {
            TRequestContextProto result;
            if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                result.set_l7_request_id(std::move(*value));
            }
            result.set_user_ip(GetRandValueT<TString>(randIn, {"10.10.10.10", "2a02:6b8:b040:3500:0:0:0:500"}));
            result.set_user_time_stamp(GetRandValueT<ui64>(randIn, {}));
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"lenta.ru", "yandex.ru"})) {
                result.set_proxy_host(std::move(*value));
            }
            result.set_is_yandex_internal(GetRandValueT<bool>(randIn, {}));

            for (unsigned char c = 0, end = 3; c < end; ++c) {
                (*result.mutable_cgi_params())[to_lower(ToString(GetRandEnumIntValue<ECgiParam>(randIn)))] = GetRandValueT<TString>(randIn, {});
            }
            for (const auto it : GetEnumAllValues<ECgiParam>()) {
                const TString key = to_lower(ToString(it));
                switch (it) {
                    case ECgiParam::dp: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"1", "1.5", "2", "3", "4"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::screen_size:
                    case ECgiParam::size: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"640,480", "100,500"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::poiy: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"500", "100"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::app_id: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"app_id"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::did: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"SomId_FFAABBCC"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::uuid: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"3a01dd11b3ae046f4947659512e8af61"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::hardware_did: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"SomId_FFAABBCC"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::oauth: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"SomeId_FFAABBCC"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::app_platform: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"windows", "android", "ios", "windowsphone", "unknown"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::app_version: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"6030500", "1020400", "000000000", "001000000"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::os_version: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"10.2", "5.4", "3.1"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::clid: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"123-456.789", "987-456.789", "777-123.789"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::win: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"789", "56", "77"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::geo: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"213", "10000", "66", "51", "3", "187"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::local_datetime: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"2019-11-22T04:30:27"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::old_browser_mode: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::browser_name: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"Opera", "YandexSearch", "Chome", "YandexBrowser"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::browser_version: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"22.1", "19.2", "10.2", "5.4", "3.1"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::is_touch: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::is_mobile: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::is_tablet: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::is_tv: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::is_wap: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::yandexuid: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"124340581456504425", "124340288745650425", "143240288868650425"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::traffic_level: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"17.9,18.10,19.5"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::traffic_rate: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"8", "3"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::yx_news_morda_rubric: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"sport", "music"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    case ECgiParam::sens: {
                        if (auto value = GetRandMaybeValueT<TString>(randIn, {"230", "000", "999"})) {
                            (*result.mutable_cgi_params())[key] = *value;
                        }
                    } break;
                    default:
                        ythrow yexception() << "The ECgiParam::" << ToString(it) << " not added to fuzzy";
                        break;
                }
            }

            for (unsigned char c = 0, end = 3; c < end; ++c) {
                (*result.mutable_cookies())[to_lower(GetRandValueT<TString>(randIn, {}))].set_value(GetRandValueT<TString>(randIn, {}));
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"L_cookie"})) {
                (*result.mutable_cookies())[to_lower(TString("L"))].set_value(*value);
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"session_id"})) {
                (*result.mutable_cookies())[to_lower(TString("Session_id"))].set_value(*value);
            }

            for (unsigned char c = 0, end = 3; c < end; ++c) {
                (*result.mutable_http_headers())[to_lower(GetRandValueT<TString>(randIn, {}))] = GetRandValueT<TString>(randIn, {});
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"OAuth someauthdata"})) {
                (*result.mutable_http_headers())[to_lower(TString("Authorization"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"10.10.10.10"})) {
                (*result.mutable_http_headers())[to_lower(TString("X-Forwarded-For"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"yummy_cookie=choco; tasty_cookie=strawberry"})) {
                (*result.mutable_http_headers())[to_lower(TString("COOKIE"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"reqId"})) {
                (*result.mutable_http_headers())[to_lower(TString("X-REQUEST-ID"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"other value", "Yandex TAPOC"})) {
                (*result.mutable_http_headers())[to_lower(TString("Via"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"lenta.ru", "yandex.ru"})) {
                (*result.mutable_http_headers())[to_lower(TString("X-Proxy-Host"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                (*result.mutable_http_headers())[to_lower(TString("X-Yandex-ICookie"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                (*result.mutable_http_headers())[to_lower(TString("X-Yandex-ExpFlags"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                (*result.mutable_http_headers())[to_lower(TString("X-Yandex-ExpBoxes"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"11.11.11.11"})) {
                (*result.mutable_http_headers())[to_lower(TString("X-Real-IP"))] = *value;
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"12.12.12.12"})) {
                (*result.mutable_http_headers())[to_lower(TString("X-Forwarded-For-Y"))] = *value;
            }

            TUserAgentProto& userAgent = *(result.mutable_user_agent());
            if (auto value = GetRandMaybeValueT<bool>(randIn, {true, false})) {
                userAgent.set_is_tablet(*value);
            }
            if (auto value = GetRandMaybeValueT<bool>(randIn, {true, false})) {
                userAgent.set_is_mobile(*value);
            }
            if (auto value = GetRandMaybeValueT<bool>(randIn, {true, false})) {
                userAgent.set_is_touch(*value);
            }
            if (auto value = GetRandMaybeValueT<bool>(randIn, {true, false})) {
                userAgent.set_is_tv(*value);
            }
            if (auto value = GetRandMaybeValueT<bool>(randIn, {true, false})) {
                userAgent.set_is_wap(*value);
            }
            if (auto value = GetRandMayBeEnumIntValue<EOSFamily>(randIn)) {
                if (EOSFamily_IsValid(*value)) {
                    userAgent.set_os_family(static_cast<EOSFamily>(*value));
                }
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"Safari", "Edge", "Opera", "YandexSearch", "Chome", "YandexBrowser"})) {
                userAgent.set_browser_name(*value);
            }
            if (auto value = GetRandMaybeValueT<TNumberedVersion>(randIn, {})) {
                *(userAgent.mutable_browser_version()) = value->ToNumberedVersionProto();
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"Chromium", "MSIE", "Firefox"})) {
                userAgent.set_browser_engine(*value);
            }
            if (auto value = GetRandMaybeValueT<TNumberedVersion>(randIn, {})) {
                *(userAgent.mutable_browser_engine_version()) = value->ToNumberedVersionProto();
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {"Presto", "Gecko", "WebKit"})) {
                userAgent.set_browser_base(*value);
            }
            if (auto value = GetRandMaybeValueT<TNumberedVersion>(randIn, {})) {
                *(userAgent.mutable_browser_base_version()) = value->ToNumberedVersionProto();
            }

            if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                userAgent.set_app_id(*value);
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                userAgent.set_device_id(*value);
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                userAgent.set_hardware_device_id(*value);
            }
            if (auto value = GetRandMaybeValueT<TString>(randIn, {})) {
                userAgent.set_device_uuid(*value);
            }
            if (auto value = GetRandMaybeValueT<float>(randIn, {1., 1.5, 2., 2.5, 3., 4.})) {
                userAgent.set_scale_factor(*value);
            }
            if (GetRandValueT<bool>(randIn, {})) {
                const ui32 width = GetRandValueT<ui32>(randIn, {640, 100, 1024});
                const ui32 height = GetRandValueT<ui32>(randIn, {480, 500, 968});
                userAgent.mutable_screen_dimensions()->set_width(width);
                userAgent.mutable_screen_dimensions()->set_height(height);
            }
            result.set_is_old_browser_mode(GetRandValueT<bool>(randIn, {}));

            result.mutable_my_cookie(); // TODO(art-snake): fill values

            Y_ENSURE(result.IsInitialized(), TString("Not all required fields was filled: ") + result.InitializationErrorString());
            return result;
        }

        NJson::TJsonValue OverrideValues(NJson::TJsonValue src, const NJson::TJsonValue& overrides) {
            if (!overrides.IsMap())
                return src;
            for (const auto& it : overrides.GetMapSafe()) {
                src[it.first] = it.second;
            }
            return src;
        }

    } // namespace

    TFuzzBlockRunner::TFuzzBlockRunner() = default;

    TFuzzBlockRunner::~TFuzzBlockRunner() = default;

    void TFuzzBlockRunner::SetStaticRequestLegacyData(NJson::TJsonValue value) {
        StaticRequestLegacyData_ = std::move(value);
    }

    void TFuzzBlockRunner::SetStaticRequestData(const TRequestContextProto& proto) {
        StaticRequestData_ = proto;
    }

    void TFuzzBlockRunner::ProcessFuzzRequest(const uint8_t* data, size_t size) {
        auto randGen = size > sizeof(ui64) ? std::make_unique<TRandGenerator>(reinterpret_cast<const ui64*>(data), size / sizeof(ui64)) : std::make_unique<TRandGenerator>(0);
        TRequestContextProto request = CreateRequestPart(*randGen);
        TMemoryInput inpLegacy(data, size);
        NJson::TJsonValue legacyRequest = CreateRequestLegacyPart(inpLegacy);
        {
            // first test without static fields:
            auto context = MakeIntrusive<TTestContext>(NJson::JSON_ARRAY);
            context->AddProtobufItem(request, REQUEST_CONTEXT_PROTO_APPHOST_CTX_TYPE);
            context->AddItem(NJson::TJsonValue(legacyRequest), REQUEST_SECTION_NAME_LEGACY);
            ProcessRequest(context);
            for (const auto& it : Blocks())
                EXPECT_TRUE(context->FindFirstItem(it.get()->BlockName() + "_formatted"));
        }

        {
            // Test with static fields:
            legacyRequest = OverrideValues(legacyRequest, StaticRequestLegacyData_);
            request.MergeFrom(StaticRequestData_);
            auto context = MakeIntrusive<TTestContext>(NJson::JSON_ARRAY);
            context->AddProtobufItem(request, REQUEST_CONTEXT_PROTO_APPHOST_CTX_TYPE);
            context->AddItem(NJson::TJsonValue(legacyRequest), REQUEST_SECTION_NAME_LEGACY);
            ProcessRequest(context);
            for (const auto& it : Blocks()) {
                EXPECT_TRUE(context->FindFirstItem(it.get()->BlockName() + "_formatted"));
                //TODO: test for show == true
            }
        }
    }

} // namespace NMordaBlocks
