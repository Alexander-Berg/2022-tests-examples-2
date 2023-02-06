#include <robot/zora/postprocessing/protos/io.pb.h>
#include <zora/spider/proto/spider.pb.h>
#include <zora/zora/proto/zora.pb.h>

#include <util/string/subst.h>
#include <util/stream/output.h>
#include <util/folder/filelist.h>
#include <util/stream/file.h>
#include <google/protobuf/text_format.h>

int main(int, char**) {
    TFileList fileList;
    TString inputDir = "in";
    fileList.Fill(inputDir);

    for (size_t i=0; i < fileList.Size(); i++) {
        TString fileName(fileList.Next());
        TString filePath = inputDir  + "/" +  fileName;
        TFileInput fi(filePath);
        TString txt = fi.ReadAll();

        NProtos::TInput ti;
        if (!fileName.StartsWith("host")) {
            NZoraPb::TZoraResponse zresp;
            auto res = zresp.ParseFromString(txt);

            if (!res) {
                NProtoBuf::TextFormat::Parser parser;
                parser.ParseFromString(txt, &zresp);
            }
            ti.SetZoraResponse(zresp.SerializeAsString());
        } else {
            NSpiderPb::TSpiderHostStateNotification spiderHostNotification;
            auto res = spiderHostNotification.ParseFromString(txt);

            if(!res) {
                NProtoBuf::TextFormat::Parser parser;
                parser.ParseFromString(txt, &spiderHostNotification);
            }
            ti.SetZoraHostNotification(spiderHostNotification.SerializeAsString());
        }

        Cout << ti.DebugString() << Endl << "===" << Endl;
    }

    return 0;
}

