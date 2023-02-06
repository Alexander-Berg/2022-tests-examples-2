#include <robot/rthub/misc/porto.h>

#include <util/stream/output.h>

using namespace NRTHub;

int main(int /*argc*/, const char** /*argv*/) {
    Cout << "Querying CPU guarantee... ";
    auto const cpuGuarantee = GetCpuGuarantee();
    if (!cpuGuarantee.Defined()) {
        Cout << "Failed." << Endl;
    } else {
        Cout << "Done. CPU guarantee = " << cpuGuarantee.GetRef() << Endl;
    }
    Cout << "Querying stats... ";
    auto const stats = GetContainerStats();
    if (!stats.Defined()) {
        Cout << "Failed." << Endl;
        return 0;
    }
    Cout << "Done:" << Endl;
    Cout << "\tMemory limit: " << stats->MemoryLimit << Endl;
    Cout << "\tMemory usage: " << stats->MemoryUsage << Endl;
    Cout << "\tAnonymous memory usage: " << stats->AnonUsage << Endl;
    Cout << "\tCache memory usage: " << stats->CacheUsage << Endl;
    Cout << "\tCpu guarantee: " << stats->CpuGuarantee << Endl;
    return 0;
}
