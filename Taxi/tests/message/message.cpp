#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <iostream>
#include <string>
#include <vector>

#include <taxi/tools/dorblu/lib/include/message.h>
#include <taxi/tools/dorblu/lib/include/tokenizer.h>

#include <taxi/tools/dorblu/lib/tests/helpers.h>

TEST(Message, MessageTest)
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

    auto bsonFilter = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto rule1 = Rule(bson::object("name", "myRule1", "filter", bsonFilter));
    auto rule2 = Rule(bson::object("name", "myRule2", "filter", bsonFilter));

    Message message;
    message.setSecondsToParse(30);
    message.addRule(std::move(rule1));
    message.addRule(std::move(rule2));

    message.indexFields(t);

    for (const auto& line : inputLines) {
        message.match(*t.tokenize(line));
    }

    const auto& rules = message.rules();
    const auto& okRps1 = rules.at(0).stats().requests().at("maps_ok_rps.rps");
    const auto& okRps2 = rules.at(1).stats().requests().at("maps_ok_rps.rps");

    EXPECT_EQ(static_cast<uint64_t>(5), okRps1.count());
    EXPECT_EQ(static_cast<uint64_t>(5), okRps2.count());

    std::string& serialized = message.getSerialized();
    auto deserialized = Message();
    deserialized.setFromSerialized(serialized);

    EXPECT_EQ(message, deserialized);

    auto bsonBadnessRule = bson::object(
        "type", "And",
        "children", bson::array(
            bson::object("type", "GreaterThan", "field", "status", "operand", "499"),
            bson::object("type", "LessThan",    "field", "status", "operand", "600")
        )
    );
    auto bsonCheck = bson::object("vhost500", bson::object("MatchRule", bsonBadnessRule));

    auto mon = std::make_shared<Monitoring>(bsonCheck);

    message.addMonitoring(mon);

    message.addHostStat("stat1", 0.15);
    message.addHostStat("stat42", 42);

    std::string& serializedMon = message.getSerialized();
    auto deserializedMon = Message();
    deserializedMon.setFromSerialized(serializedMon);

    EXPECT_EQ(message, deserializedMon);
}
