#include <kikimr/persqueue/sdk/deprecated/cpp/v1/pq.h>
#include <zora/spider/proto/spider.pb.h>
#include <zora/xcalc/object/proto/object.pb.h>
#include <zora/zora/proto/zora.pb.h>

#include <util/generic/hash_set.h>
#include <util/stream/buffered.h>
#include <util/stream/file.h>
#include <util/stream/output.h>
#include <util/stream/str.h>



int main(int, char**) {
    using namespace NPersQueue2;
    TPQLib pqLib;
    TSettings settings;

    settings.ServerHostname = "vla.logbroker.yandex.net";
    settings.Topic = "zora";
    settings.LogType = "new-pp";
    settings.FileName = "samovar-dev-1";

    auto consumer = pqLib.CreateConsumer(settings, nullptr);
    consumer.Wait();
    auto reader = consumer.GetValue();

    int fileIdx = 1;
    int kiwiPipelineCnt = 0, kiwiPipelineThreashold = 500;
    int kiwiPipelineImgCnt = 0, kiwiPipelineImgThreashold = 100;
    int kiwiPipelineSitemapCnt = 0, kiwiPipelineSitemapThreashold = 100;
    int videoRotorCnt = 0;
    int hostNotificationCnt = 0, hostNotificationThreashold = 100;

    THashSet<TString> emits;
    while (kiwiPipelineCnt < kiwiPipelineThreashold ||
            kiwiPipelineImgCnt < kiwiPipelineImgThreashold ||
            kiwiPipelineSitemapCnt < kiwiPipelineSitemapThreashold ||
            hostNotificationCnt < hostNotificationThreashold) {

        Cout << "current progress: " << Endl;
        Cout << " kiwiPipelineCnt: " << kiwiPipelineCnt <<
                " kiwiPipelineImgCnt: " << kiwiPipelineImgCnt <<
                " kiwiPipelineSitemapCnt: " << kiwiPipelineSitemapCnt <<
                " hostNotificationCnt: " << hostNotificationCnt << Endl;

        auto data = reader.first->Read(10, Max<ui32>());

        auto val = data.GetValueSync();
        auto vec = val.Data.Get();

        for (auto p: *vec) {
            TString str;
            p.AsString(str);
            NXCalcProto::TObject object;
            object.ParseFromString(str);

            TString zoraResponse;
            TString zoraEmitName;
            TString zoraHostNotification;

            for (size_t j = 0; j < object.AttributesSize(); ++j) {
                auto& attr = object.GetAttributes(j);

                if (attr.GetName() == "ZoraResponse") {
                    zoraResponse = attr.GetValueBytes();
                }

                if (attr.GetName() == "ZoraEmitName") {
                    zoraEmitName = attr.GetValueString();
                    emits.insert(zoraEmitName);
                }

                if (attr.GetName() == "ZoraHostNotification") {
                    zoraHostNotification = attr.GetValueBytes();
                }
            }

            for (auto e:emits) {
                Cout << e << " ";
            }
            Cout << Endl;

            NZoraPb::TZoraResponse tZoraResponse;
            NSpiderPb::TSpiderHostStateNotification tSpiderHostStateNotification;

            TString data;
            TStringStream ss;
            ss << "out/";

            if (zoraEmitName == "ZoraKiwiHostsPipeline") {
                NSpiderPb::TSpiderHost tSpiderHost;
                tSpiderHost.ParseFromString(zoraHostNotification);
                auto mhost = tSpiderHostStateNotification.MutableHost();
                *mhost = tSpiderHost;

                Cout << tSpiderHostStateNotification.DebugString();

                hostNotificationCnt++;
                if (hostNotificationCnt > hostNotificationThreashold)
                    continue;
                data = tSpiderHostStateNotification.SerializeAsString();
                ss << "host_";
            } else {
                if (zoraEmitName == "ZoraKiwiPipeline") {
                    tZoraResponse.ParseFromString(zoraResponse);
                    kiwiPipelineCnt++;
                    if (kiwiPipelineCnt > kiwiPipelineThreashold)
                        continue;
                    ss << "pipeline_";
                } else if (zoraEmitName == "ZoraKiwiImgPipeline") {
                    tZoraResponse.ParseFromString(zoraResponse);
                    kiwiPipelineImgCnt++;
                    if (kiwiPipelineImgCnt > kiwiPipelineImgThreashold)
                        continue;
                    ss << "img_";
                } else if (zoraEmitName == "ZoraKiwiSitemapPipeline") {
                    tZoraResponse.ParseFromString(zoraResponse);
                    kiwiPipelineSitemapCnt++;
                    if (kiwiPipelineSitemapCnt > kiwiPipelineSitemapThreashold)
                        continue;
                    ss << "sitemap_";
                } else if (zoraEmitName == "VideoRotorPipeline") {
                    tZoraResponse.ParseFromString(zoraResponse);
                    videoRotorCnt++;
                    ss << "video_";
                } else {
                    continue;
                }
                data = tZoraResponse.SerializeAsString();
            }

            ss << fileIdx;
            fileIdx ++;

            TFileOutput fo(ss.Str());
            fo.Write(data);
            fo.Flush();
            fo.Finish();
        }
    }
    return 0;
}
