#include <csignal>
#include <fstream>
#include <thread>

int main(int /* argc */, char* argv[]) {
    signal(SIGTERM, SIG_IGN);
    { std::ofstream t(argv[1]); }
    std::this_thread::sleep_for(std::chrono::minutes(24 * 60));
    exit(0);
}
