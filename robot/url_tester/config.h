#pragma once

#include <robot/samovar/protos/config.pb.h>

#include <util/generic/string.h>

class TConfig {
public:
    TConfig(int argc, const char *argv[]);

public:
    TString Url;
    TString Host;
    NSamovarConfig::TInstanceConfig InstanceConfig;
    NSamovarConfig::TCombustorConfig CombustorConfig;
};
