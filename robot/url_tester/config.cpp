#include "config.h"

#include <library/cpp/getopt/opt.h>
#include <library/cpp/protobuf/util/pb_io.h>


TConfig::TConfig(int argc, const char *argv[]) {
    TString instanceConfigPath;
    TString combustorConfigPath;

    NLastGetopt::TOpts opts;
    opts.AddLongOption('u', "url", "url to work with")
        .RequiredArgument("URL")
        .StoreResult(&Url);
    opts.AddLongOption('h', "host", "host to work with. Lookup if url is not specified")
        .RequiredArgument("HOST")
        .StoreResult(&Host);
    opts.AddLongOption('c', "combustor-config", "combustor config file")
        .RequiredArgument("CombustorConfig")
        .DefaultValue("conf/conf-devel/combustor_config.pb.txt")
        .StoreResult(&combustorConfigPath);
    opts.AddLongOption('i', "instance-config", "instance config file")
        .RequiredArgument("InstanceConfig")
        .DefaultValue("conf/conf-primary-arnold/instance_config.pb.txt")
        .StoreResult(&instanceConfigPath);
    opts.AddHelpOption();
    opts.AddVersionOption();

    NLastGetopt::TOptsParseResult res(&opts, argc, argv);

    ParseFromTextFormat(combustorConfigPath, CombustorConfig);
    ParseFromTextFormat(instanceConfigPath, InstanceConfig);
}
