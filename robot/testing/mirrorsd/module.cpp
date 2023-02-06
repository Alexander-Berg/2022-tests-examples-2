#include "module.h"

#include <robot/library/url/canonizer/canonizer.h>

#include <kernel/urlnorm/normalize.h>
#include <library/cpp/messagebus/ybus.h>

#include <util/generic/yexception.h>
#include <util/generic/string.h>
#include <util/generic/vector.h>

TGeminiMirrorsdModule::TGeminiMirrorsdModule(NBus::TBusMessageQueue* queue, const TMirrorsdConfig& mirrorsdConfig)
    : NBus::TBusModule("GEMINICASTORMODULE")
    , Config(mirrorsdConfig)
    , MirrorsdProtocol(Config.Port)
{
    NGemini::TUrlCanonizer::TConfig config;
    config.MirrorsTriePath = Config.MirrorsPath;
    config.MirrorsReloaderEnable = true;
    config.MirrorsPrechargeMode = PCHM_Force_Lock;

    Canonizer.Reset(new NGemini::TUrlCanonizer(config));

    MirrorsdServerSessionConfig.MaxInFlight = Config.MaxInFlightJobs;
    MirrorsdServerSessionConfig.SendTimeout = TDuration::Seconds(20).MilliSeconds();
    MirrorsdServerSessionConfig.TotalTimeout = 2 * MirrorsdServerSessionConfig.SendTimeout;
    MirrorsdServerSessionConfig.MaxBufferSize = 128 * 1024;
    if (!NBus::TBusModule::CreatePrivateSessions(queue)) {
        ythrow yexception() << "TGeminiMirrorsdModule::TGeminiMirrorsdModule: CreatePrivateSessions failed";
    }
}

TGeminiMirrorsdModule::~TGeminiMirrorsdModule() {
    /* no-op */
}

void TGeminiMirrorsdModule::Start() {
    if (!TBusModule::StartInput()) {
        ythrow yexception() << "TGeminiMirrorsdModule::Start: StartInput failed";
    }
}

bool TGeminiMirrorsdModule::Shutdown() {
    return TBusModule::Shutdown();
}

NBus::TBusServerSessionPtr TGeminiMirrorsdModule::CreateExtSession(NBus::TBusMessageQueue& queue) {
    return CreateDefaultDestination(queue, &MirrorsdProtocol, MirrorsdServerSessionConfig);
}

NBus::TJobHandler TGeminiMirrorsdModule::Start(NBus::TBusJob* job, NBus::TBusMessage* msg) {
    TGeminiCastorRequest* req = dynamic_cast<TGeminiCastorRequest *>(msg);
    Y_VERIFY(!!req, "Incoming request is NULL.");

    TAutoPtr<TGeminiCastorResponse> resp(new TGeminiCastorResponse);

    try {
        TString normUrl = DoWeakUrlNormalization(req->Record.GetUrl());

        TString errMessage;
        if (!Canonizer->IsValidUrl(normUrl, errMessage)) {
            resp->Record.SetOriginalUrl(req->Record.GetUrl());
            resp->Record.SetErrorMessage(errMessage);
            resp->Record.SetError(NGeminiOldProtos::BAD_URL);

            job->SendReply(resp);

            return nullptr;
        }

        if (req->Record.GetCanonizationType() == NGeminiOldProtos::MIRROR) {
            ui32 info = 0;
            TString result;
            Canonizer->CanonizeUrl(normUrl, NGemini::CT_MIRRORS, info, result);

            resp->Record.SetCanonizationType(req->Record.GetCanonizationType());
            resp->Record.SetOriginalUrl(req->Record.GetUrl());
            resp->Record.SetMainMirror(result);
        } else {
            resp->Record.SetOriginalUrl(req->Record.GetUrl());
            resp->Record.SetErrorMessage("Unknown canonization type");
            resp->Record.SetError(NGeminiOldProtos::UNKNOWN_ERROR);
        }

        job->SendReply(resp);
        return nullptr;
    } catch (const NGemini::TParseException& excp) {
        resp->Record.SetOriginalUrl(req->Record.GetUrl());
        resp->Record.SetErrorMessage(excp.what());
        resp->Record.SetError(NGeminiOldProtos::BAD_URL);

        job->SendReply(resp);
        return nullptr;
    } catch (...) {
        resp->Record.SetOriginalUrl(req->Record.GetUrl());
        resp->Record.SetErrorMessage(CurrentExceptionMessage());
        resp->Record.SetError(NGeminiOldProtos::UNKNOWN_ERROR);

        job->SendReply(resp);
        return nullptr;
    }
}
