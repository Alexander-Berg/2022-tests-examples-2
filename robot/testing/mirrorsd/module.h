#pragma once

#include "config.h"

#include <robot/library/url/canonizer/canonizer.h>
#include <robot/deprecated/gemini/protos/castorproto.h>
#include <library/cpp/messagebus/ybus.h>

class TGeminiMirrorsdModule : public NBus::TBusModule {
public:
    TGeminiMirrorsdModule(NBus::TBusMessageQueue* queue, const TMirrorsdConfig& config);
    virtual ~TGeminiMirrorsdModule();

    void Start();

    virtual bool Shutdown();

    virtual NBus::TBusServerSessionPtr CreateExtSession(NBus::TBusMessageQueue& queue);

    virtual NBus::TJobHandler Start(NBus::TBusJob* job, NBus::TBusMessage* msg);

private:
    const TMirrorsdConfig& Config;

    THolder<NGemini::TUrlCanonizer> Canonizer;

    NBus::TBusSessionConfig MirrorsdServerSessionConfig;

    TGeminiCastorProtocol MirrorsdProtocol;
};
