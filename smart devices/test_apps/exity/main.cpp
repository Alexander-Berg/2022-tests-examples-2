#include <chrono>
#include <iostream>
#include <random>
#include <thread>

int main() {
    std::mt19937_64 eng{std::random_device{}()}; // or seed however you want
    std::uniform_int_distribution<> dist{100, 2000};
    std::this_thread::sleep_for(std::chrono::milliseconds{dist(eng)});
    unsigned int exitcode = dist(eng) % 2;
    exit(exitcode);
}
