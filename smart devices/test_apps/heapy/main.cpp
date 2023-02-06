#include <chrono>
#include <cstdlib>
#include <iostream>
#include <random>
#include <thread>

int main() {
    int* allocd = new int[1024 * 1024];
    for (int i = 0; i < 1024 * 1024; i++) {
        allocd[i] = i;
    }
    std::mt19937_64 eng{std::random_device{}()};
    std::uniform_int_distribution<> dist{100, 2000};
    std::this_thread::sleep_for(std::chrono::milliseconds{dist(eng)});
    delete[] allocd;
    exit(EXIT_SUCCESS);
}
