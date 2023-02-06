#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <iostream>
#include <cmath>
#include <taxi/tools/dorblu/lib/include/stats.h>
#include <taxi/tools/dorblu/lib/include/tokenizer.h>

#include <taxi/tools/dorblu/lib/tests/helpers.h>

template <class T>
struct SomethingAndValue
{
    SomethingAndValue() {}
    SomethingAndValue(T &&t, double e): subject(std::move(t)), expectedValue(e) {}
    T subject;
    double expectedValue;
};

std::ostream& operator<<(std::ostream& os, const Stats& s)
{
    return os << (std::string)s;
}

template <class T>
bool matchVectors(std::vector<T> expected, std::vector<T> got)
{
    auto vectorToString = [](std::vector<T> v) -> std::string {
        if (v.size() == 0)
            return "()";

        std::stringstream repr;
        repr << "(";
        for (auto it = v.begin(), end = v.end() - 1; it != end; ++it) {
            repr << *it << ", ";
        }
        repr << v.back() << ")";

        return repr.str();
    };

    auto compareVectors = [](std::vector<T> v1, std::vector<T> v2) -> bool {
        if (v1.size() != v2.size())
            return false;

        for (size_t i = 0; i < v1.size(); ++i) {
            if (v1[i] != v2[i])
                return false;
        }

        return true;
    };

    if (compareVectors(expected, got)) {
        std::cout << "ok." << std::endl;
        return true;
    } else {
        std::cout << "failed." << std::endl;
        std::cout << "Expected " << vectorToString(expected) << ", but got " << vectorToString(got) <<std::endl;
        return false;
    }
}

bool matchInts(int64_t expected, int64_t got)
{
    if (expected == got) {
        std::cout << "ok." << std::endl;
        return true;
    } else {
        std::cout << "failed." << std::endl;
        std::cout << "Expected " << expected << ", but got " << got <<std::endl;
        return false;
    }
}

bool matchDoubles(double expected, double got)
{
    double thresh = 0.00001;
    double diff = std::fabs(std::fabs(expected) - std::fabs(got));

    if (diff < thresh) {
        std::cout << "ok." << std::endl;
        return true;
    } else {
        std::cout << "failed." << std::endl;
        std::cout << "Expected " << expected << ", but got " << got <<std::endl;
        return false;
    }
}

TEST(Stats, ApdexCaseTest)
{
    std::vector<float> testTimings = {
        0.1, 0.1, 0.15, 0.6, 0.01, 0.5,
        0.8, 0.0001, 0.3, 0.99, 0.5
    };

    /* Test 1: Apdex calculations */
    std::map<std::string, SomethingAndValue<Apdex>> apdex;
    apdex["default"]                           = { Apdex(), 0 };
    apdex["one argument (0.1)"]                = { Apdex(0.1), 0.318182 };
    apdex["two arguments (0.1, 0.15)"]         = { Apdex(0.1, 0.15), 0.272727 };
    apdex["definitely ok (15)"]                = { Apdex(15), 1 };
    apdex["definitely not ok (0.2)"]           = { Apdex(0.2), 0.5 };

    std::cout << "Apdex<default> without data: ";
    matchDoubles(1, apdex["default"].subject.value());

    for (auto& a : apdex) {
        for (auto t : testTimings) {
            a.second.subject.match(t);
        }
    }

    for (const auto& a : apdex) {
        std::cout << "Apdex<" << a.first << ">: ";
        EXPECT_TRUE(matchDoubles(a.second.expectedValue, a.second.subject.value()));
    }

    /* Test 2: Apdex sum */
    Apdex& toSum = apdex["definitely not ok (0.2)"].subject;
    Apdex sum;
    sum += toSum;
    sum += toSum;

    std::cout << "Sum of two apdexes: comparing <ok>: ";
    EXPECT_TRUE(matchInts(toSum.ok() * 2, sum.ok()));
    std::cout << "Sum of two apdexes: comparing <tolerated>: ";
    EXPECT_TRUE(matchInts(toSum.tolerated() * 2, sum.tolerated()));
    std::cout << "Sum of two apdexes: comparing <total>: ";
    EXPECT_TRUE(matchInts(toSum.total() * 2, sum.total()));

    /* Test 3: Apdex serialization */
    DorBluPB::Apdex pbApdex;
    Apdex& victim = apdex["definitely not ok (0.2)"].subject;
    victim.setType(TimingsType::req);
    victim.setPrefix("apdex.req");
    victim.serializeTo(&pbApdex);
    Apdex deserialized(pbApdex);

    std::cout << "Comparing apdexes before serialization and after deserialization: ";
    EXPECT_TRUE(victim == deserialized);
}

TEST(Stats, HttpCodeRangeTest)
{
    std::vector<int> codes = {
        200, 200, 200, 200, 200, 500,
        200, 200, 200, 200, 200, 502,
        200, 200, 200, 200, 200, 503,
        200, 200, 200, 200, 200, 500,
        200, 200, 200, 200, 200, 500,
        400, 404, 499, 302, 301, 302
    };

    /* Test 1: Basic counting */
    std::map<std::string, SomethingAndValue<HttpCodeRange>> codeRange;
    codeRange["default"] = { HttpCodeRange(), 0 };
    codeRange["2xx"]     = { HttpCodeRange(200, 299), 25 };
    codeRange["5xx"]     = { HttpCodeRange(500, 599), 5 };
    codeRange["400"]     = { HttpCodeRange(400), 1 };

    for (auto& cr : codeRange) {
        for (auto c : codes) {
            cr.second.subject.match(c);
        }
    }

    for (const auto& cr : codeRange) {
        std::cout << "HttpCodeRange <" << cr.first << ">: ";
        EXPECT_TRUE(matchInts(cr.second.expectedValue, cr.second.subject.count()));
    }

    /* Test 2: Sum of HttpCodeRanges */
    /*
    HttpCodeRange& toSum = codeRange["2xx"].subject;
    HttpCodeRange sum;
    sum += toSum;
    sum += toSum;

    std::cout << "Sum of two HttpCodeRanges: ";
    if (!matchInts(toSum.count() * 2, sum.count())) {
        return false;
    }*/

    /* Test 3: Serialization and deserialization */
    HttpCodeRange& victim = codeRange["2xx"].subject;
    victim.setPrefix("2xx.rps");
    DorBluPB::HttpCodeRange pbHttpCodeRange;
    victim.serializeTo(&pbHttpCodeRange);
    HttpCodeRange deserialized(pbHttpCodeRange, 1);

    std::cout << "Comparing HttpCodeRanges before serialization and after deserialization: ";
    EXPECT_TRUE(victim == deserialized);
}

TEST(Stats, TimingsTest)
{
    std::vector<float> testTimes = {
        0.5, 0.11, 0.2, 0.18, 15.0, 1.48
    };

    /* Test 1: creation */
    Timings timings;
    for (auto t : testTimes) {
        timings.push_back(t);
    }

    timings.addLimits(0.5, 0.2, 5.0);

    std::cout << "Matching Timings to self: ";
    EXPECT_TRUE(matchVectors(timings.timings(), timings.timings()));

    /* Test 2: serialize/deserialize */
    timings.setType(TimingsType::req);
    timings.setPrefix("timins.req");
    DorBluPB::Timings pbTimings;
    timings.serializeTo(&pbTimings);
    Timings deserialized(pbTimings);

    std::cout << "Comparing Timings before serialization and after deserialization: ";
    EXPECT_TRUE(timings == deserialized);
}

TEST(Stats, BytesCounterTest)
{
    std::vector<int64_t> testBytes = { 200, 100, 10, 15, 1000 };
    auto testBytesSum = [&testBytes] {
        int64_t sum = 0;
        for (auto x : testBytes)
            sum += x;
        return sum;
    };

    /* Test 1: creation */
    BytesCounter bc;
    for (auto b : testBytes) {
        bc.addValue(b);
    }

    TestEquals("BytesCounter value", testBytesSum(), bc.counter());
    TestEquals("Matching BytesCounter to self", bc, bc);

    bc.setPrefix("blah");

    DorBluPB::BytesCounter pbBytesCounter;
    bc.serializeTo(&pbBytesCounter);
    auto deserialized = BytesCounter(pbBytesCounter, 1);

    TestEquals("BytesCounter [de]serialization", bc, deserialized);
}

TEST(Stats, CacheRateTest)
{
    std::unordered_map<std::string, int64_t> values{
        {"HIT", 15}, {"MISS", 5}, {"-", 100},
        {"EXPIRED", 1}, {"REVALIDATED", 2},
        {"UPDATING", 3}, {"BYPASS", 4}, {"STALE", 5},
        {"some_illegal_id", 22}
    };

    CacheRate cr;

    for (const auto& val : values) {
        for (int i = 0; i < val.second; ++i) {
            cr.addValue(val.first);
        }
    }

    const auto& counters = cr.counters();

    for (const auto& v : {"HIT", "MISS", "EXPIRED", "REVALIDATED", "UPDATING", "BYPASS", "STALE"}) {
          TestEquals(v, values.at(v), counters.at(v));
    }
    TestEquals("None", values.at("-") + values.at("some_illegal_id"), counters.at("NONE"));
}

TEST(Stats, StatsTest)
{
    Tokenizer t("files/basic_log_format.conf", false);

    std::vector<std::string> inputLines = {
        "\"GET /foo HTTP/1.1\" 200 0.100 \"0.098\" -",
        "\"GET /foo HTTP/1.1\" 200 0.200 \"0.198\" -",
        "\"GET /foo HTTP/1.1\" 200 0.150 \"0.148\" -",
        "\"GET /foo HTTP/1.1\" 200 0.100 \"0.098\" -",
        "\"GET /foo HTTP/1.1\" 200 0.500 \"0.498\" -",
        "\"GET /foo HTTP/1.1\" 302 0.100 \"0.098\" -",
        "\"GET /foo HTTP/1.1\" 500 0.100 \"0.098\" -",
        "\"GET /bar HTTP/1.1\" 200 0.100 \"0.098\" -",
        "\"GET /bar HTTP/1.1\" 200 0.200 \"0.198\" -",
        "\"GET /bar HTTP/1.1\" 200 0.300 \"0.298\" -"
    };
    /* Test 1: basic creation */
    Stats stats;

    stats.addHttpRange("rps.2xx", HttpCodeRange(200, 299));
    stats.addHttpRange("rps.400", HttpCodeRange(400));
    stats.addHttpRange("rps.404", HttpCodeRange(404));
    stats.addHttpRange("rps.499", HttpCodeRange(499));
    stats.addHttpRange("rps.5xx", HttpCodeRange(500, 599));

    stats.addApdex("apdex.req", Apdex(0.100), TimingsType::req);
    stats.addApdex("apdex.ups", Apdex(0.100), TimingsType::ups);
    stats.addApdex("apdex.ssl", Apdex(0.100), TimingsType::ssl);

    stats.addTimings("timings.req", Timings(), TimingsType::req);
    stats.addTimings("timings.ups", Timings(), TimingsType::ups);
    stats.addTimings("timings.ssl", Timings(), TimingsType::ssl);

    stats.addCacheRate("cache", CacheRate());

    stats.indexFields(t);

    for (const auto& line : inputLines) {
        auto result = t.tokenize(line);
        ASSERT_TRUE(result);
        stats.addLine(*result, false);
    }

    YasmMetrics metrics;
    stats.addYasmMetrics("test", &metrics);
    std::stringstream ss;
    ss << metrics;

    /* Test 2: [de]serialization */
    DorBluPB::Stats pb_stats;
    stats.serializeTo(&pb_stats);
    Stats stats2(pb_stats, 1);
    std::cout << "Serializing and deserializing stats: ";
    EXPECT_TRUE(stats == stats2);
}
