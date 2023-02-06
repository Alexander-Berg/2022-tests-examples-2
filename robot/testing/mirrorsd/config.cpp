#include "config.h"

#include <library/cpp/svnversion/svnversion.h>
#include <util/system/hostname.h>
#include <util/stream/format.h>

#undef STORED_NUM
#define STORED_NUM(name)    RequiredArgument("N").DefaultValue(ToString(name).data()).StoreResult(&name)

TMirrorsdConfig::TMirrorsdConfig(int argc, char** argv) {
    Daemonize = true;
    Host = FQDNHostName();
    Port = 20000;
    MaxInFlightJobs = 2000000;
    NumWorkers = 3;

    NLastGetopt::TOpts opts;
    opts.AddLongOption('v', "version",          "print version").NoArgument();
    opts.AddLongOption('w', "numworkers",       "number of workers for pollux module").
            RequiredArgument("NUM").DefaultValue("3").StoreResult(&NumWorkers);
    opts.AddLongOption('m', "max-in-fl",        "maximum number of in-flight jobs").STORED_NUM(MaxInFlightJobs);
    opts.AddLongOption('h', "host",             "gemini server host").
            RequiredArgument("HOST").DefaultValue(Host).StoreResult(&Host);
    opts.AddLongOption('p', "port",             "port").
            RequiredArgument("NUM").DefaultValue("20000").StoreResult(&Port);
    opts.AddLongOption("no-daemon",             "don't daemonize").NoArgument();
    opts.AddLongOption("mirrors-path",          "path to mirrors file").
            RequiredArgument("PATH").StoreResult(&MirrorsPath);

    opts.AddHelpOption();

    NLastGetopt::TOptsParseResult res(&opts, argc, argv);

    if (res.Has('v')) {
        Cerr << PROGRAM_VERSION << Endl;
        exit(1);
    }

    if (res.Has("no-daemon")) {
        Daemonize = false;
    }
}

#undef STORED_NUM

#undef DUMP_FIELD
#define DUMP_FIELD(param)     out << LeftPad(#param, 32) << ":  " << param << Endl;

void TMirrorsdConfig::DumpConfig(IOutputStream& out) const {
    DUMP_FIELD(Daemonize);
    DUMP_FIELD(Host);
    DUMP_FIELD(Port);
    DUMP_FIELD(MaxInFlightJobs)
    DUMP_FIELD(NumWorkers);
    out << Endl;
}

#undef DUMP_FIELD
