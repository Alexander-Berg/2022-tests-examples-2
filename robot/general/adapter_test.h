#pragma once

#include <util/system/defaults.h>

namespace NOxygen {

class TTupleAdapterTester {
private:
    bool RandomSeed;
    size_t TestsNum;

    void DoPerformTest(ui32 seed);
public:
    TTupleAdapterTester(bool randomSeed);

    void PerformTest();
};

} // namespace NOxygen
