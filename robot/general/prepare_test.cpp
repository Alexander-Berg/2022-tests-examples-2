#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <mapreduce/yt/interface/client.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/getopt/modchooser.h>

#include <google/protobuf/text_format.h>

#include <util/draft/datetime.h>
#include <util/random/random.h>
#include <library/cpp/string_utils/url/url.h>


int ParseCrawlAttempt(int argc, const char** argv);
int MakeUnbiased(int argc, const char** argv);
int CalcHostLimit(int argc, const char** argv);
int JoinFactors(int argc, const char** argv);
int JoinSpam(int argc, const char** argv);
int JoinUserdata(int argc, const char** argv);
int MarkDnsSpam(int argc, const char** argv);
int CalcBorders(int argc, const char** argv);
int GetSearchBaseInfo(int argc, const char** argv);
int MakeRRTestPoolLabels(int argc, const char** argv);
int CalcRRFactors(int argc, const char** argv);
int CreateEntryWithLabel(int argc, const char** argv);
int FetchHostBorders(int argc, const char** argv);
int ApplyRemap(int argc, const char** argv);
int AddReferrerLabels(int argc, const char** argv);
int MergeData(int argc, const char** argv);
int ShrinkPool(int argc, const char** argv);


int PrepareTest(int argc, const char** argv) {
    TModChooser modeChooser;
    modeChooser.AddMode("parse-crawlattempt", ParseCrawlAttempt, "parse crawl attempt log");
    modeChooser.AddMode("make-unbiased-pool", MakeUnbiased, "make unbiased by policy pool");
    modeChooser.AddMode("calc-host-limit", CalcHostLimit, "calc host limit");
    modeChooser.AddMode("join-factors", JoinFactors, "join factors");
    modeChooser.AddMode("join-userdata", JoinUserdata, "join userdata");
    modeChooser.AddMode("join-spam", JoinSpam, "join spam");
    modeChooser.AddMode("mark-dns-spam", MarkDnsSpam, "join dns spam");
    modeChooser.AddMode("calc-borders", CalcBorders, "calc borders");
    modeChooser.AddMode("get-search-base-info", GetSearchBaseInfo, "get data from search base");
    modeChooser.AddMode("set-rr-labels", MakeRRTestPoolLabels, "make labels for rr test pool labels");
    modeChooser.AddMode("calc-rr-factors", CalcRRFactors, "calc factors for rr");
    modeChooser.AddMode("create-entry-with-label", CreateEntryWithLabel, "create pool entry with specified label");
    modeChooser.AddMode("fetch-host-borders", FetchHostBorders, "fetch host borders");
    modeChooser.AddMode("apply-remap", ApplyRemap, "apply remap");
    modeChooser.AddMode("add-referrer-labels", AddReferrerLabels, "add edr labels for refferrer");
    modeChooser.AddMode("merge-data", MergeData, "merge data");
    modeChooser.AddMode("shrink-pool", ShrinkPool, "shrink pool to disire size");

    modeChooser.Run(argc, argv);
    return 0;
}
