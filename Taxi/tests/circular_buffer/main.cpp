#include <taxi/graph/libs/circular_buffer/circular_buffer.h>
#include <util/stream/output.h>
#include <limits>
#include <random>
#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>
#include <deque>

template <typename T>
using TCircularBuffer = NTaxi::NCircularBuffer::TCircularBuffer<T>;

struct TCircularBufferFixture: public ::NUnitTest::TBaseTestCase {
    TCircularBufferFixture() {
        generator.seed(42);
    }

    size_t GetRandomNumber(size_t lower = 0, size_t upper = std::numeric_limits<size_t>::max()) {
        std::uniform_int_distribution<size_t> rng(lower, upper);
        return rng(generator);
    }

    void FillAndCheckIteratorsOutput(const size_t capacity, const size_t totalAmount, bool rvalue = false) {
        std::deque<size_t> etalon;
        TCircularBuffer<size_t> buff(capacity);

        for (size_t i = 0; i < totalAmount; ++i) {
            size_t value = GetRandomNumber();
            if (rvalue) {
                buff.PushBack(std::move(value));
            } else {
                buff.PushBack(value);
            }
            etalon.push_back(value);
            if (etalon.size() > capacity) {
                etalon.pop_front();
            }
        }
        UNIT_ASSERT_EQUAL_C(etalon.size(), buff.Size(), "Etalon size " << etalon.size() << " vs buff size " << buff.Size());

        // prefix increment
        {
            std::vector<size_t> outEtalon;
            std::vector<size_t> outBuff;
            outEtalon.reserve(capacity);
            outBuff.reserve(capacity);
            const TCircularBuffer<size_t>& const_ref = buff;
            for (auto it = etalon.begin(); it != etalon.end(); ++it) {
                outEtalon.push_back(*it);
            }
            for (auto it = const_ref.begin(); it != const_ref.end(); ++it) {
                outBuff.push_back(*it);
                UNIT_ASSERT_LE(outBuff.size(), outEtalon.size());
            }
            UNIT_ASSERT_EQUAL_C(outEtalon.size(), outBuff.size(), "Out etalon size " << outEtalon.size() << " vs out buff size " << outBuff.size());
            auto etalonIt = outEtalon.begin();
            auto buffIt = outBuff.begin();
            while (etalonIt != outEtalon.end() && buffIt != outBuff.end()) {
                UNIT_ASSERT_EQUAL_C(*buffIt, *etalonIt, "Etalon value " << *etalonIt << " vs buff value " << *buffIt);
                ++etalonIt;
                ++buffIt;
            }
        }
        // postfix increment
        {
            std::vector<size_t> outEtalon;
            std::vector<size_t> outBuff;
            outEtalon.reserve(capacity);
            outBuff.reserve(capacity);
            for (auto it = etalon.begin(); it != etalon.end(); ++it) {
                outEtalon.push_back(*it);
            }
            for (auto it = buff.begin(); it != buff.end(); it++) {
                outBuff.push_back(*it);
                UNIT_ASSERT_LE(outBuff.size(), outEtalon.size());
            }
            UNIT_ASSERT_EQUAL_C(outEtalon.size(), outBuff.size(), "Out etalon size " << outEtalon.size() << " vs out buff size " << outBuff.size());
            auto etalonIt = outEtalon.begin();
            auto buffIt = outBuff.begin();
            while (etalonIt != outEtalon.end() && buffIt != outBuff.end()) {
                UNIT_ASSERT_EQUAL_C(*buffIt, *etalonIt, "Etalon value " << *etalonIt << " vs buff value " << *buffIt);
                ++etalonIt;
                ++buffIt;
            }
        }
        // reverse iterator
        {
            std::vector<size_t> outEtalon;
            std::vector<size_t> outBuff;
            outEtalon.reserve(capacity);
            outBuff.reserve(capacity);
            for (auto it = etalon.rbegin(); it != etalon.rend(); ++it) {
                outEtalon.push_back(*it);
                ;
            }
            for (auto it = buff.rbegin(); it != buff.rend(); it++) {
                outBuff.push_back(*it);
                UNIT_ASSERT_LE(outBuff.size(), outEtalon.size());
            }
            UNIT_ASSERT_EQUAL_C(outEtalon.size(), outBuff.size(), "Out etalon size " << outEtalon.size() << " vs out buff size " << outBuff.size());
            auto etalonIt = outEtalon.begin();
            auto buffIt = outBuff.begin();
            while (etalonIt != outEtalon.end() && buffIt != outBuff.end()) {
                UNIT_ASSERT_EQUAL_C(*buffIt, *etalonIt, "Etalon value " << *etalonIt << " vs buff value " << *buffIt);
                ++etalonIt;
                ++buffIt;
            }
        }
        // const reverse iterator
        {
            std::vector<size_t> outEtalon;
            std::vector<size_t> outBuff;
            outEtalon.reserve(capacity);
            outBuff.reserve(capacity);
            for (auto it = etalon.rbegin(); it != etalon.rend(); ++it) {
                outEtalon.push_back(*it);
                ;
            }
            const TCircularBuffer<size_t>& const_ref = buff;
            for (auto it = const_ref.rbegin(); it != const_ref.rend(); it++) {
                outBuff.push_back(*it);
                UNIT_ASSERT_LE(outBuff.size(), outEtalon.size());
            }
            UNIT_ASSERT_EQUAL_C(outEtalon.size(), outBuff.size(), "Out etalon size " << outEtalon.size() << " vs out buff size " << outBuff.size());
            auto etalonIt = outEtalon.begin();
            auto buffIt = outBuff.begin();
            while (etalonIt != outEtalon.end() && buffIt != outBuff.end()) {
                UNIT_ASSERT_EQUAL_C(*buffIt, *etalonIt, "Etalon value " << *etalonIt << " vs buff value " << *buffIt);
                ++etalonIt;
                ++buffIt;
            }
        }
        // prefix decrement
        {
            std::vector<size_t> outEtalon;
            std::vector<size_t> outBuff;
            outEtalon.reserve(capacity);
            outBuff.reserve(capacity);
            for (auto it = etalon.rbegin(); it != etalon.rend(); ++it) {
                outEtalon.push_back(*it);
            }
            for (auto it = buff.end(); it != buff.begin(); --it) {
                auto next = it;
                --next;
                outBuff.push_back(*next);
                UNIT_ASSERT_LE(outBuff.size(), outEtalon.size());
            }
            UNIT_ASSERT_EQUAL_C(outEtalon.size(), outBuff.size(), "Out etalon size " << outEtalon.size() << " vs out buff size " << outBuff.size());
            auto etalonIt = outEtalon.begin();
            auto buffIt = outBuff.begin();
            while (etalonIt != outEtalon.end() && buffIt != outBuff.end()) {
                UNIT_ASSERT_EQUAL_C(*buffIt, *etalonIt, "Etalon value " << *etalonIt << " vs buff value " << *buffIt);
                ++etalonIt;
                ++buffIt;
            }
        }
        // postfix decrement
        {
            std::vector<size_t> outEtalon;
            std::vector<size_t> outBuff;
            outEtalon.reserve(capacity);
            outBuff.reserve(capacity);
            for (auto it = etalon.rbegin(); it != etalon.rend(); ++it) {
                outEtalon.push_back(*it);
            }
            for (auto it = buff.end(); it != buff.begin(); it--) {
                auto next = it;
                next--;
                outBuff.push_back(*next);
                UNIT_ASSERT_LE(outBuff.size(), outEtalon.size());
            }
            UNIT_ASSERT_EQUAL_C(outEtalon.size(), outBuff.size(), "Out etalon size " << outEtalon.size() << " vs out buff size " << outBuff.size());
            auto etalonIt = outEtalon.begin();
            auto buffIt = outBuff.begin();
            while (etalonIt != outEtalon.end() && buffIt != outBuff.end()) {
                UNIT_ASSERT_EQUAL_C(*buffIt, *etalonIt, "Etalon value " << *etalonIt << " vs buff value " << *buffIt);
                ++etalonIt;
                ++buffIt;
            }
        }
    }

    void CompareBuffers(TCircularBuffer<size_t>& first, TCircularBuffer<size_t>& second) {
        std::vector<size_t> firstOut, secondOut;
        for (const auto& v : first) {
            firstOut.push_back(v);
        }
        for (const auto& v : second) {
            secondOut.push_back(v);
        }

        UNIT_ASSERT_EQUAL(firstOut.size(), secondOut.size());
        for (size_t i = 0; i < firstOut.size(); ++i) {
            UNIT_ASSERT_EQUAL(firstOut[i], secondOut[i]);
        }
    }
    std::mt19937 generator;
};

Y_UNIT_TEST_SUITE_F(CircularBufferTestFixture, TCircularBufferFixture) {
    // Basic check
    Y_UNIT_TEST(Test1) {
        // prime number
        const size_t capacity = 1009;
        // prime number
        const size_t totalAmount = 93407;

        FillAndCheckIteratorsOutput(capacity, totalAmount);
        FillAndCheckIteratorsOutput(capacity, totalAmount, true);
    }

    // More big check
    Y_UNIT_TEST(Test2) {
        // prime number
        const size_t capacity = 100609;
        // prime number
        const size_t totalAmount = 102197;

        FillAndCheckIteratorsOutput(capacity, totalAmount);
        FillAndCheckIteratorsOutput(capacity, totalAmount, true);
    }

    // Zero capacity
    Y_UNIT_TEST(ZeroCapacity) {
        const size_t capacity = 0;
        // prime number
        const size_t totalAmount = 102197;

        FillAndCheckIteratorsOutput(capacity, totalAmount);

        // check push back for zero capacity
        TCircularBuffer<size_t> buff(0);
        buff.PushBack(42);
        UNIT_ASSERT_EQUAL(buff.Size(), 0);
        UNIT_ASSERT_EQUAL(buff.begin(), buff.end());
    }

    // Zero total amount
    Y_UNIT_TEST(ZeroTotalAmount) {
        // prime number
        const size_t capacity = 100609;
        const size_t totalAmount = 0;

        FillAndCheckIteratorsOutput(capacity, totalAmount);
    }

    // Copy, move
    Y_UNIT_TEST(CopyMove) {
        TCircularBuffer<size_t> orig(10);
        for (size_t i = 0; i < 20; ++i) {
            orig.PushBack(i);
        }
        UNIT_ASSERT_EQUAL(orig.Size(), 10);
        UNIT_ASSERT_EQUAL(orig.IsFull(), true);
        UNIT_ASSERT_EQUAL(orig.IsEmpty(), false);

        {
            TCircularBuffer<size_t> copy(orig);
            CompareBuffers(orig, copy);
        }
        {
            TCircularBuffer<size_t> copy(0);
            copy = orig;
            CompareBuffers(orig, copy);
        }
        {
            TCircularBuffer<size_t> copy1(orig);
            TCircularBuffer<size_t> copy2(std::move(copy1));
            CompareBuffers(orig, copy2);
        }
        {
            TCircularBuffer<size_t> copy1(orig);
            TCircularBuffer<size_t> copy2(0);
            copy2 = std::move(copy1);
            CompareBuffers(orig, copy2);
        }
    }

    // Clear
    Y_UNIT_TEST(Clear) {
        TCircularBuffer<size_t> orig(10);
        for (size_t i = 0; i < 20; ++i) {
            orig.PushBack(i);
        }
        UNIT_ASSERT_EQUAL(orig.Size(), 10);
        UNIT_ASSERT_EQUAL(orig.IsFull(), true);
        UNIT_ASSERT_EQUAL(orig.IsEmpty(), false);

        orig.Clear();
        UNIT_ASSERT_EQUAL(orig.Size(), 0);
        UNIT_ASSERT_EQUAL(orig.IsFull(), false);
        UNIT_ASSERT_EQUAL(orig.IsEmpty(), true);

        std::vector<size_t> dump;
        for (const auto& v : orig) {
            dump.push_back(v);
        }
        UNIT_ASSERT(dump.empty());
    }

    // Iterator dereference and copy
    Y_UNIT_TEST(Dereference) {
        struct Item {
            size_t Value = 5;
        };

        TCircularBuffer<Item> buff(2, true);
        Item item1{1};
        Item item2{10};
        buff.PushBack(item1);
        buff.PushBack(item2);
        auto it = buff.begin();
        ++it;

        UNIT_ASSERT_EQUAL((*it).Value, 10);
        UNIT_ASSERT_EQUAL(it->Value, 10);

        {
            TCircularBuffer<Item>::iterator it2(it);
            UNIT_ASSERT_EQUAL(it2->Value, it->Value);
        }
        {
            TCircularBuffer<Item>::iterator it2;
            it2 = it;
            UNIT_ASSERT_EQUAL(it2->Value, it->Value);
        }
    }

    // front/back
    Y_UNIT_TEST(FrontAndBack) {
        TCircularBuffer<size_t> buff(5, true);
        for (size_t i = 0; i < 10; ++i) {
            buff.PushBack(i);
        }
        UNIT_ASSERT_EQUAL(buff.back(), 9);
        UNIT_ASSERT_EQUAL(buff.front(), 5);
    }

    // Stress test 1
    Y_UNIT_TEST(Stress1) {
        const size_t capacity = GetRandomNumber(10e2, 10e3);
        size_t totalAmount = GetRandomNumber(capacity, 10e4);

        FillAndCheckIteratorsOutput(capacity, totalAmount);
        FillAndCheckIteratorsOutput(0, totalAmount);
        FillAndCheckIteratorsOutput(capacity, 0);
    }

    // Stress test 2
    Y_UNIT_TEST(Stress2) {
        const size_t capacity = GetRandomNumber(10e6, 10e7);
        size_t totalAmount = GetRandomNumber(capacity, 10e9);
        FillAndCheckIteratorsOutput(capacity, totalAmount);
    }

    // Stress test 3
    Y_UNIT_TEST(Stress3) {
        const size_t capacity = GetRandomNumber(10e3, 10e4);
        size_t totalAmount = GetRandomNumber(capacity, 10e6);
        FillAndCheckIteratorsOutput(capacity, totalAmount);
    }
}
