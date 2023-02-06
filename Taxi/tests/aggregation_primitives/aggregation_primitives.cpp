#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <taxi/tools/dorblu/lib/include/aggregation_primitives.h>
#include <taxi/tools/dorblu/lib/include/graphite.h>

#include <taxi/tools/dorblu/lib/tests/helpers.h>

bool isInMetrics(const std::string& line, const GraphiteMetrics& metr)
{
    for (const auto& m : metr.rawMetrics()) {
        if (m == line) {
            std::cout << "ok." << std::endl;
            return true;
        }
    }

    std::cout << "failed." << std::endl;
    std::cout << "Expected: " << line << std::endl;
    std::cout << "But it is not in:" << std::endl;
    for (const auto& m : metr.rawMetrics()) {
        std::cout << m << std::endl;
    }

    return false;
}

TEST(AggregationPrimitives, HttpCodeAggregatorTest)
{
    HttpCodeAggregator aggr;

    auto stuffCodes = [](HttpCodeRange& hcr) {
        for (auto code : { 200, 200, 400, 500, 400, 302, 200 }) {
            hcr.match(code);
        }
    };

    auto range1 = HttpCodeRange(200, 299);
    range1.setPrefix("2xx");
    stuffCodes(range1);
    aggr.addHttpCodes(range1);
    aggr.addHttpCodes(range1);

    auto range2 = HttpCodeRange(400);
    range2.setPrefix("400");
    stuffCodes(range2);

    aggr.addHttpCodes(range2);
    aggr.addHttpCodes(range2);

    const auto& codeRanges = aggr.codeRanges();

    std::cout << "2xx total: ";
    EXPECT_EQ(static_cast<uint64_t>(6), static_cast<uint64_t>(codeRanges.at("2xx") * 60));

    std::cout << "400 total: ";
    EXPECT_EQ(static_cast<uint64_t>(4), static_cast<uint64_t>(codeRanges.at("400") * 60));

    GraphiteMetrics grMetrics;
    SolomonSpack solomon;
    aggr.aggregate(grMetrics, solomon);

    std::cout << "2xx graphite metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....2xx 0.100000", grMetrics));
    std::cout << "400 graphite metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....400 0.066667", grMetrics));
}

TEST(AggregationPrimitives, ApdexAggregatorTest)
{
    ApdexAggregator aggr;

    auto stuffTimes = [](Apdex& a) {
        for (auto time : { 0.098, 0.098, 0.150, 0.140, 0.980, 0.101, 1.0 }) {
            a.match(time);
        }
    };

    auto apdex1 = Apdex(0.100, 0.200);
    apdex1.setPrefix("ups_apdex");
    stuffTimes(apdex1);
    aggr.addApdex(apdex1);
    aggr.addApdex(apdex1);

    auto apdex2 = Apdex(0.150, 0.300);
    apdex2.setPrefix("req_apdex");
    stuffTimes(apdex2);
    aggr.addApdex(apdex2);
    aggr.addApdex(apdex2);

    const auto& apdexes = aggr.apdexes();

    std::cout << "ups_apdex oks : ";
    EXPECT_EQ(static_cast<uint64_t>(4), apdexes.at("ups_apdex").ok());
    std::cout << "req_apdex oks: ";
    EXPECT_EQ(static_cast<uint64_t>(8), apdexes.at("req_apdex").ok());

    GraphiteMetrics grMetrics;
    SolomonSpack solomon;
    aggr.aggregate(grMetrics, solomon);

    std::cout << "ups_apdex graphite metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....req_apdex 0.642857", grMetrics));
    std::cout << "req_apdex graphite metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....ups_apdex 0.500000", grMetrics));
}

TEST(AggregationPrimitives, TimingsAggregatorTest)
{
    TimingsAggregator aggr;

    DorBluPB::Timings pbTimings; //we neet it to correctly sort timings

    Timings timings1;
    timings1.setPrefix("upstream_time");
    timings1.setType(TimingsType::ups);
    for (auto t : { 0.001, 0.001, 0.002, 0.002, 0.002, 0.003, 0.003, 0.003, 0.003, 0.004 }) {
        timings1.push_back(t);
    }
    timings1.serializeTo(&pbTimings);

    Timings timings2;
    timings2.setPrefix("upstream_time");
    timings2.setType(TimingsType::ups);
    for (auto t : { 0.011, 0.011, 0.012, 0.012, 0.012, 0.013, 0.013, 0.013, 0.013, 0.014 }) {
        timings2.push_back(t);
    }
    timings2.serializeTo(&pbTimings);

    Timings timings3;
    timings3.setPrefix("upstream_time");
    timings3.setType(TimingsType::ups);
    for (auto t : { 0.111, 0.112, 0.112, 0.112, 0.112, 0.113, 0.113, 0.113, 0.114, 0.114 }) {
        timings3.push_back(t);
    }
    timings3.serializeTo(&pbTimings);

    aggr.addTimings(timings1);
    aggr.addTimings(timings2);
    aggr.addTimings(timings3);

    GraphiteMetrics grMetrics;
    SolomonSpack solomon;
    aggr.aggregate(grMetrics, solomon);

    std::cout << "upstream_time.99_prc graphite metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....upstream_time.99_prc 114", grMetrics));
    std::cout << "upstream_time.90_prc graphite metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....upstream_time.90_prc 113", grMetrics));
    std::cout << "upstream_time.75_prc metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....upstream_time.75_prc 112", grMetrics));

    EXPECT_TRUE(aggr.timingsTypeIndex().at(TimingsType::ups) == "upstream_time");
}

TEST(AggregationPrimitives, BytesCounterAggregatorTest)
{
    std::vector<int64_t> bcInput = { 100, 200, 300 };
    int64_t bcInputSum = 0;
    std::vector<BytesCounter> bc;
    for (auto x : bcInput) {
        bcInputSum += x;

        BytesCounter bytesCounter;
        bytesCounter.addValue(x);
        bc.emplace_back(std::move(bytesCounter));
    }

    BytesCounterAggregator bcAggr;
    for (auto& b : bc)
        bcAggr.addBytesCounter(b);

    TestEquals("BytesCounterAggregator summarized counter", bcInputSum, static_cast<int64_t>(bcAggr.bytesCounters().at("")) * 60);
}

TEST(AggregationPrimitives, CacheRateAggregatorTest)
{
    std::unordered_map<std::string, int64_t> values1{
        {"HIT", 15}, {"MISS", 5}, {"-", 100}
    };
    std::vector<CacheRate> rates(2);

    for (auto val : { "HIT", "HIT", "HIT", "HIT", "HIT", "MISS", "MISS" }) {
        rates[0].addValue(val);
    }
    for (auto val : { "MISS", "MISS", "MISS", "MISS", "MISS", "HIT", "HIT" }) {
        rates[1].addValue(val);
    }

    CacheRateAggregator crAggr;
    for (const auto& r : rates) {
        crAggr.addCacheRate(r);
    }

    EXPECT_NEAR(crAggr.cacheRates().at(".HIT"), 7./60., 1e-10);
    EXPECT_NEAR(crAggr.cacheRates().at(".MISS"), 7./60., 1e-10);
}

TEST(AggregationPrimitives, RuleAggregatorTest)
{
    Tokenizer t("files/basic_log_format.conf", false);
    std::vector<std::string> inputLines = {
        "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -",
        "\"GET /ping HTTP/1.1\" 200 0.200 \"0.198\" -",
        "\"GET /ping HTTP/1.1\" 200 0.150 \"0.148\" -",
        "\"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -",
        "\"GET /ping HTTP/1.1\" 200 0.500 \"0.498\" -",
        "\"GET /ping HTTP/1.1\" 302 0.100 \"0.098\" -",
        "\"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "\"GET /bar HTTP/1.1\" 200 0.100 \"0.098\" -",
        "\"GET /bar HTTP/1.1\" 200 0.200 \"0.198\" -",
        "\"GET /bar HTTP/1.1\" 200 0.300 \"0.298\" -"
    };

    DorBluPB::Rule pbRule; // for proper sorting, that takes place during serialization

    auto bsonFilter = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto bsonApdex = bson::object("Ups", 100, "Req", 100);
    auto bsonOptions = bson::object("Apdex", bsonApdex);
    auto rule1 = Rule(bson::object("name", "myRule1", "filter", bsonFilter, "Options", bsonOptions));
    auto rule2 = Rule(bson::object("name", "myRule2", "filter", bsonFilter, "Options", bsonOptions));
    rule1.indexFields(t);
    rule2.indexFields(t);
    for (const auto& line : inputLines) {
        auto result = *t.tokenize(line);
        rule1.match(result, false);
        rule2.match(result, false);
    }
    rule1.serializeTo(&pbRule);
    rule2.serializeTo(&pbRule);

    RuleAggregator aggr;
    aggr.addRule(rule1);
    aggr.addRule(rule2);

    GraphiteMetrics grMetrics;
    SolomonSpack solomon;
    aggr.aggregate(grMetrics, solomon);

    std::cout << "maps_ok_request_timings.95_prc of RuleAggregator metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....maps_ok_request_timings.95_prc 500", grMetrics));
    std::cout << "maps_ok_ssl_timings.99_prc of RuleAggregator metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....maps_ok_ssl_timings.99_prc 0", grMetrics));
    std::cout << "maps_ok_rps.rps of RuleAggregator metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo....maps_ok_rps.rps 0.166667", grMetrics));
}

TEST(AggregationPrimitives, RegionAggregatorTest)
{
    auto portHolder = NTesting::GetFreePort();
    int port = static_cast<int>(portHolder);
    auto host1 = getHost(port);
    auto host2 = getHost(port);
    auto host3 = getHost(port, "myOtherRule");
    RegionAggregator aggr;
    aggr.addHost(host1);
    aggr.addHost(host2);
    aggr.addHost(host3);

    GraphiteMetrics grMetrics;
    SolomonSpack solomon;
    aggr.aggregate(grMetrics, solomon);

    std::cout << "maps_ok_request_timings.95_prc of RegionAggregator myRule metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo...myRule.maps_ok_request_timings.95_prc 500", grMetrics));
    std::cout << "maps_ok_ssl_timings.99_prc of RegionAggregator myRule metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo...myRule.maps_ok_ssl_timings.99_prc 0", grMetrics));
    std::cout << "maps_ok_rps.rps of RegionAggregator myRule metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo...myRule.maps_ok_rps.rps 0.166667", grMetrics));

    std::cout << "maps_ok_request_timings.95_prc of RegionAggregator myOtherRule metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo...myOtherRule.maps_ok_request_timings.95_prc 500", grMetrics));
    std::cout << "maps_ok_ssl_timings.99_prc of RegionAggregator myOtherRule metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo...myOtherRule.maps_ok_ssl_timings.99_prc 0", grMetrics));
    std::cout << "maps_ok_rps.rps of RegionAggregator myOtherRule metrics: ";
    EXPECT_TRUE(isInMetrics("cluster.geo...myOtherRule.maps_ok_rps.rps 0.083333", grMetrics));
}
