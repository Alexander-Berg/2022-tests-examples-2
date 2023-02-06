#include "config.h"
#include "module.h"

#include <library/cpp/messagebus/ybus.h>

#include <cstdlib>
#include <signal.h>
#include <unistd.h>

int main(int argc, char** argv) {
    TMirrorsdConfig config(argc, argv);

    if (config.Daemonize) {
        if (daemon(0, 1) == -1) {
            exit(EXIT_FAILURE);
        }

        if (signal(SIGHUP, SIG_IGN) == SIG_ERR) {
            exit(EXIT_FAILURE);
        }
    }

    if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) {
        exit(EXIT_FAILURE);
    }

    // Block signals before creating any threads
    sigset_t sigset;
    sigemptyset(&sigset);
    sigaddset(&sigset, SIGINT);
    sigaddset(&sigset, SIGTERM);
    if (sigprocmask(SIG_SETMASK, &sigset, nullptr) == -1) {
        exit(EXIT_FAILURE);
    }

    NBus::TBusQueueConfig busQueueConfig;
    busQueueConfig.NumWorkers = config.NumWorkers;
    NBus::TBusMessageQueuePtr busQueue = CreateMessageQueue(busQueueConfig);
    THolder<TGeminiMirrorsdModule> busModule(new TGeminiMirrorsdModule(busQueue.Get(), config));
    busModule->Start();

    // Wait for SIGINT or SIGTERM
    sigwaitinfo(&sigset, nullptr);

    busModule->Shutdown();
    busModule.Reset(nullptr);

    return 0;
}
