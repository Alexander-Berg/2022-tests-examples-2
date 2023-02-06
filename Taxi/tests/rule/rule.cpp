#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <iostream>
#include <string>
#include <vector>

#include <taxi/tools/dorblu/lib/include/rule.h>
#include <taxi/tools/dorblu/lib/include/tokenizer.h>

std::ostream& operator<<(std::ostream& os, const Rule& r)
{
    return os << (std::string)r;
}

void stuffRule(Rule& rule)
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
    rule.indexFields(t);

    for (const auto& line : inputLines) {
        rule.match(*t.tokenize(line), false);
    }
}

TEST(Rule, BasicRuleTest)
{
    auto bsonFilter = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto bsonRule = bson::object("name", "myRule", "filter", bsonFilter);
    auto basicRule = Rule(bsonRule);
    stuffRule(basicRule);

    const auto& basicStats = basicRule.stats();
    const auto& basicOkRps = basicStats.requests().at("maps_ok_rps.rps");
    const auto& basicRequestTimings = basicStats.timings().at("maps_ok_request_timings");

    std::cout << "maps_ok_rps.rps in basic rule: ";
    EXPECT_EQ(static_cast<uint64_t>(5), basicOkRps.count());

    std::cout << "maps_ok_request_timings in basic rule: ";
    EXPECT_EQ(static_cast<size_t>(5), basicRequestTimings.timings().size());
}

TEST(Rule, ApdexRuleTest)
{
    auto bsonFilter = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto bsonApdex = bson::object("Ups", 100, "Req", 100);
    auto bsonOptions = bson::object("Apdex", bsonApdex);
    auto bsonRule = bson::object("name", "myRule", "filter", bsonFilter, "Options", bsonOptions);
    auto rule = Rule(bsonRule);
    stuffRule(rule);

    const auto& apdexStats = rule.stats();
    const auto& apdexOkRps = apdexStats.requests().at("maps_ok_rps.rps");
    const auto& apdexRequestTimings = apdexStats.timings().at("maps_ok_request_timings");
    const auto& apdexUps = apdexStats.apdexes().at("ups_apdex.ups_apdex");
    const auto& apdexReq = apdexStats.apdexes().at("req_apdex.req_apdex");

    std::cout << "maps_ok_rps.rps in apdex rule: ";
    EXPECT_EQ(static_cast<uint64_t>(5), apdexOkRps.count());

    std::cout << "maps_ok_request_timings in apdex rule: ";
    EXPECT_EQ(static_cast<size_t>(5), apdexRequestTimings.timings().size());

    std::cout << "ups_apdex.ups_apdex oks in apdex rule: ";
    EXPECT_EQ(static_cast<uint64_t>(2), apdexUps.ok());
    std::cout << "ups_apdex.ups_apdex tolerated in apdex rule: ";
    EXPECT_EQ(static_cast<uint64_t>(2), apdexUps.tolerated());

    std::cout << "req_apdex.req_apdex oks in apdex rule: ";
    EXPECT_EQ(static_cast<uint64_t>(0), apdexReq.ok());
    std::cout << "req_apdex.req_apdex tolerated in apdex rule: ";
    EXPECT_EQ(static_cast<uint64_t>(3), apdexReq.tolerated());
}

TEST(Rule, CustomHttpRuleTest)
{
    auto bsonFilter = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto bsonCustomHttp = bson::array(302, bson::array(300, 304));
    auto bsonOptions = bson::object("CustomHttp", bsonCustomHttp);
    auto bsonRule = bson::object("name", "myRule", "filter", bsonFilter, "Options", bsonOptions);
    auto rule = Rule(bsonRule);
    stuffRule(rule);

    const auto& httpStats = rule.stats();

    const auto& httpOkRps = httpStats.requests().at("maps_ok_rps.rps");
    const auto& httpRequestTimings = httpStats.timings().at("maps_ok_request_timings");
    const auto& http302 = httpStats.requests().at("maps_errors_302_rps.rps");
    const auto& http300_304 = httpStats.requests().at("maps_300_304_rps.rps");

    std::cout << "maps_ok_rps.rps in customhttp rule: ";
    EXPECT_EQ(static_cast<uint64_t>(5), httpOkRps.count());

    std::cout << "maps_ok_request_timings in customhttp rule: ";
    EXPECT_EQ(static_cast<size_t>(5), httpRequestTimings.timings().size());

    std::cout << "maps_errors_302_rps.rps oks in customhttp rule: ";
    EXPECT_EQ(static_cast<uint64_t>(1), http302.count());
    std::cout << "maps_300_304_rps.rps tolerated in customhttp rule: ";
    EXPECT_EQ(static_cast<uint64_t>(1), http300_304.count());
}

TEST(Rule, RuleSerializationTest)
{
    auto bsonFilter = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto bsonCustomHttp = bson::array(302, bson::array(300, 304));
    auto bsonOptions = bson::object("CustomHttp", bsonCustomHttp);
    auto bsonRule = bson::object("name", "myRule", "filter", bsonFilter, "Options", bsonOptions);
    auto rule = Rule(bsonRule);
    stuffRule(rule);

    std::cout << "Rule equals to itself: ";
    EXPECT_EQ(rule, rule);

    DorBluPB::Rule pb_rule;
    rule.serializeTo(&pb_rule);
    auto deserialized = Rule(pb_rule, 1);

    std::cout << "Deserialized Rule equals to original one: ";
    EXPECT_EQ(rule, deserialized);
}
