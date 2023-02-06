#include "config.h"

#include <robot/samovar/algo/locator/locator.h>
#include <robot/samovar/algo/misc/logfile.h>
#include <robot/samovar/algo/record/host_record.h>
#include <robot/samovar/algo/record/url_record.h>

#include <robot/samovar/algo/crawl/border_maintainer.h>
#include <robot/samovar/algo/crawl/crawlconfig.h>
#include <robot/samovar/algo/crawl/limiter.h>
#include <robot/samovar/algo/crawl/throttler.h>

#include <robot/samovar/algo/samovar_url_data/samovar_url_data.h>

#include <robot/samovar/algo/feeds/feeds_config.h>
#include <robot/samovar/algo/globaldata/storage.h>
#include <robot/samovar/algo/globalhisto/globalhisto.h>
#include <robot/samovar/algo/host_creator/queue.h>
#include <robot/samovar/algo/host_data_cache/host_data_cache.h>
#include <robot/samovar/algo/links/config/border_maintainer.h>
#include <robot/samovar/algo/links/config/config.h>
#include <robot/samovar/algo/locator/instance_selector.h>
#include <robot/samovar/algo/misc/switchbox.h>
#include <robot/samovar/algo/models/models.h>
#include <robot/samovar/algo/push/monster_host_mantainer.h>
#include <robot/samovar/algo/rank_sampling/config.h>
#include <robot/samovar/algo/ranks/slices/producers.h>
#include <robot/samovar/algo/sampling/sampling_config.h>
#include <robot/samovar/algo/samovar_url_data/samovar_url_data.h>
#include <robot/library/zlog/monpage.h>
#include <robot/samovar/algo/zoneconfig/zoneconfig.h>
#include <robot/samovar/algo/keepconfig/keep_config.h>
#include <robot/samovar/algo/outlinkskeepconfig/out_links_keep_config.h>
#include <robot/samovar/algo/rotor/config.h>
#include <robot/samovar/algo/touch_config/touch_config.h>
#include <robot/samovar/algo/tops/top_maintainer.h>

#include <robot/samovar/algo/canonizer/canonizer.h>

#include <mapreduce/yt/interface/client.h>
#include <yt/yt/core/misc/shutdown.h>

#include <library/cpp/getopt/opt.h>
#include <library/cpp/protobuf/util/pb_io.h>

using namespace NYT;
using namespace NSamovar;

void LookupUrl(const TString& url, TUrlRecordPtr& urlRecord, THostRecordPtr& hostRecord) {
    TMaybe<TUrlKey> url_key = TUrlKey::Create(url);
    Y_VERIFY(url_key);
    NSamovarSchema::TUrlDataRow url_row;
    url_key->ToProto(url_row);

    NSamovarSchema::THostDataRow host_row;
    url_key->AsHostKey().ToProto(host_row);

    const TMaybe<NSamovarSchema::TUrlDataRow> resultUrlRow =
            TSamovarUrlData::Get()->LookupRow(url_row);
    const TMaybe<NSamovarSchema::THostDataRow> resultHostRow =
            TLocator::Get()->GetHostDataTable().LookupRow(host_row);

    Y_VERIFY(resultUrlRow);
    Y_VERIFY(resultHostRow);

    urlRecord = TUrlRecord::TryDeserialize(*resultUrlRow);
    hostRecord = THostRecord::TryDeserialize(*resultHostRow);

    Y_VERIFY(urlRecord);
    Y_VERIFY(hostRecord);

    urlRecord->Bind(*hostRecord);
}

void LookupHost(const TString& host, THostRecordPtr& hostRecord) {
    TMaybe<THostKey> host_key = THostKey::Create(host);
    Y_VERIFY(host_key);
    NSamovarSchema::THostDataRow host_row;
    host_key->ToProto(host_row);

    const TMaybe<NSamovarSchema::THostDataRow> resultHostRow =
            TLocator::Get()->GetHostDataTable().LookupRow(host_row);

    Y_VERIFY(resultHostRow);

    hostRecord = THostRecord::TryDeserialize(*resultHostRow);

    Y_VERIFY(hostRecord);
}

void InitStaticObjects(NSamovarConfig::TInstanceConfig& instanceConfig, NSamovarConfig::TCombustorConfig& combustorConfig) {
    TLocator::InitStatic(instanceConfig);
    TSamovarUrlData::InitStatic(*TLocator::Get());

    TZoneConfig::InitStatic(combustorConfig.GetZoneConfigFile());
    TCanonizer::InitStatic(combustorConfig.GetCanonizerConfigFile());
    TKeepConfig::InitStatic(combustorConfig.GetKeepConfigFile());
    TOutLinksKeepConfig::InitStatic(combustorConfig.GetOutLinksKeepConfigFile());
    TTouchConfig::InitStatic(combustorConfig.GetTouchConfigFile());
    TLinksConfig::InitStatic(combustorConfig.GetLinksConfigFile());
    TSendLinkBorderMaintainer::InitStatic(*TLinksConfig::Get());
    TCrawlConfig::InitStatic(combustorConfig.GetCrawlConfigFile(), *TZoneConfig::Get());
    TCrawlBorderMaintainer::InitStatic(*TCrawlConfig::Get());
    TRotorConfig::InitStatic(combustorConfig.GetRotorConfigFile());
    TRotorBorderMaintainer::InitStatic(*TRotorConfig::Get());
    TLimiter::InitStatic(combustorConfig.GetLimiterConfigFile());
    TCrawlThrottler::InitStatic(combustorConfig.GetMaxApplicationCrawlRate());

    NModelsController::Configure(combustorConfig.GetModelsConfigFile());
    TPushMonsterHostMantainer::InitStatic(combustorConfig.GetMonsterHostMantainerConfigFile());
    TRankSamplingConfig::InitStatic(combustorConfig.GetRankSamplingConfigFile());
    TRankSamplingBorderMaintainer::InitStatic(*TRankSamplingConfig::Get());
    TInstanceSelector::InitStatic();
    THostCreatorQueue::InitStatic();
    TFeedsConfig::InitStatic(combustorConfig.GetFeedsConfigFile());
    TSamplingConfig::InitStatic(combustorConfig.GetSamplingConfigFile());

    TTopMaintainerConfig topConfig(combustorConfig.GetTopsConfigFile());
    topConfig.StartDeltaPushWorker = false;
    topConfig.StartMergeGlobalWorker = false;
    TTopMaintainer::InitStatic(topConfig);

    TGlobalHistoConfig globalHistoConfig(combustorConfig.GetHistoConfigFile());
    globalHistoConfig.StartDeltaPushWorker = false;
    globalHistoConfig.StartMergeGlobalWorker = false;
    TGlobalHisto::InitStatic(globalHistoConfig);
}


void DestroyStaticObjects() {
    THostDataCache::DestroyStatic();
    TGlobalDataReloadableStorage::DestroyStatic();
    TGlobalHisto::DestroyStatic();
    TPushMonsterHostMantainer::DestroyStatic();
    TInstanceSelector::DestroyStatic();
    THostCreatorQueue::DestroyStatic();
    TTopMaintainer::DestroyStatic();

    TLocator::DestroyStatic();
}

int main(int argc, const char* argv[]) {
    TConfig config(argc, argv);
    InitStaticObjects(config.InstanceConfig, config.CombustorConfig);

    TUrlRecordPtr urlRecord;
    THostRecordPtr hostRecord;

    if (config.Url) {
        LookupUrl(config.Url, urlRecord, hostRecord);
    } else if(config.Host) {
        LookupHost(config.Host, hostRecord);
    }

    /*
    / your code here
    */

    DestroyStaticObjects();
    NYT::Shutdown();

    return 0;
}
