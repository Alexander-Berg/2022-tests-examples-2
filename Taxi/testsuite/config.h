#pragma once

#include <taxi/logistic-dispatcher/library/async_impl/async_impl.h>
#include <taxi/logistic-dispatcher/common_server/util/accessor.h>

#include <kernel/daemon/config/daemon_config.h>

#include <library/cpp/mediator/global_notifications/system_status.h>
#include <library/cpp/json/json_reader.h>
#include <library/cpp/logger/global/global.h>
#include <library/cpp/string_utils/url/url.h>

#include <util/stream/file.h>

class TTestsuiteClientConfig {
    RTLINE_READONLY_ACCEPTOR_DEF(Host, TString);
    RTLINE_READONLY_ACCEPTOR(Port, ui32, 80);
    RTLINE_FLAG_ACCEPTOR(TTestsuiteClientConfig, Https, false);
    RTLINE_READONLY_ACCEPTOR(RequestTimeout, TDuration, TDuration::Seconds(10));
    RTLINE_READONLY_ACCEPTOR(Route, TString, "/testpoint");
    RTLINE_READONLY_ACCEPTOR_DEF(RequestConfig, NSimpleMeta::TConfig);

public:
    void Init(const TYandexConfig::Section* section);
};
