#pragma once

#include <yweb/robot/quotalib/networking/static_parameters.h>
#include <robot/deprecated/gemini/lib/config.h>
#include <yweb/robot/kiwi/base/msgbus.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/logger/system.h>

#include <util/generic/ptr.h>
#include <util/generic/string.h>
#include <util/network/ip.h>

class TMirrorsdConfig {
public:
    TMirrorsdConfig(int argc, char** argv);

    void DumpConfig(IOutputStream& out) const;

public:
    bool Daemonize;
    TIpPort Port;
    TString Host;
    unsigned MaxInFlightJobs;
    unsigned NumWorkers;
    TString MirrorsPath;
};
