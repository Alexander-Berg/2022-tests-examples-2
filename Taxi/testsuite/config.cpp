#include "config.h"

void TTestsuiteClientConfig::Init(const TYandexConfig::Section* section) {
    Host = section->GetDirectives().Value<TString>("Host", Host);
    Port = section->GetDirectives().Value<ui32>("Port", Port);
    HttpsFlag = section->GetDirectives().Value<bool>("Https", HttpsFlag);
    RequestTimeout = section->GetDirectives().Value<TDuration>("RequestTimeout", RequestTimeout);
    Route = section->GetDirectives().Value<TString>("Route", Route);
    {
        const TYandexConfig::TSectionsMap children = section->GetAllChildren();
        {
            auto it = children.find("RequestConfig");
            if (it != children.end()) {
                RequestConfig.InitFromSection(it->second);
            }
        }
    }
}
