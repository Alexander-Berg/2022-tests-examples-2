#include <chrono>
#include <cstdlib>
#include <iostream>
#include <random>
#include <thread>

int main(int /* argc */, char* argv[]) {
    int sleep_for = std::stoi(argv[1]);
    std::this_thread::sleep_for(std::chrono::seconds{sleep_for});
    exit(EXIT_SUCCESS);
}
