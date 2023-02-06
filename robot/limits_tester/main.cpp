#include <robot/samovar/algo/crawl/limiter.h>

#include <library/cpp/protobuf/util/pb_io.h>

class TConfig {
public:
    TString ZoraLimitsFile;
    TString ZoraDistrConfigFile;
    TString LimiterConfigFile;
    TString CrawlConfigFile;

public:
    TConfig(int argc, const char *argv[]) {
        NLastGetopt::TOpts opts;
        opts.AddLongOption('l', "zora-limits", "path to zora limits file").RequiredArgument("PATH").Required().StoreResult(&ZoraLimitsFile);
        opts.AddLongOption('d', "distr-conf", "path to zora distr conf file").RequiredArgument("PATH").Required().StoreResult(&ZoraDistrConfigFile);

        opts.AddLongOption("limiter-config", "path to limiter_config file").RequiredArgument("PATH").Optional().StoreResult(&LimiterConfigFile);
        opts.AddLongOption("crawl-config", "path to crawl_config file").RequiredArgument("PATH").Optional().StoreResult(&CrawlConfigFile);

        opts.AddHelpOption();
        opts.AddVersionOption();

        NLastGetopt::TOptsParseResult(&opts, argc, argv);
    }
};

int main(int argc, const char* argv[]) {
    TConfig config(argc, argv);

    NUkrop::TZoraLimiter limiter(config.ZoraLimitsFile, config.ZoraDistrConfigFile);

    if (config.LimiterConfigFile && config.CrawlConfigFile) {
        NSamovarConfig::TLimiterConfig limiterConfig;
        ParseFromTextFormat(config.LimiterConfigFile, limiterConfig);
        limiterConfig.SetZoraLimitsFile(config.ZoraLimitsFile);
        limiterConfig.SetZoraDistrFile(config.ZoraDistrConfigFile);
        auto invalidSettings = NSamovar::TLimiter::FindCrawlsettingsWithInvalidGroups(limiterConfig, config.CrawlConfigFile);
        if (!invalidSettings.empty()) {
            TString settingsString = JoinStrings(invalidSettings.begin(), invalidSettings.end(), ", ");
            ythrow yexception() << "Missconfigurated limit group and zora source in crawlconfigs: " << settingsString;
        }
    }

    return 0;
}
