#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <taxi/tools/dorblu/lib/include/monitoring.h>
#include <taxi/tools/dorblu/lib/include/error.h>

#include <taxi/tools/dorblu/lib/tests/helpers.h>

TEST(Monitoring, CheckLimitsTest)
{
    CheckLimits cl;

    TestEquals("CheckLimits calculate severity 1", MonitoringSeverity::None,     cl.calculateSeverity(9, 3));
    TestEquals("CheckLimits calculate severity 2", MonitoringSeverity::None,     cl.calculateSeverity(10000, 70));
    TestEquals("CheckLimits calculate severity 3", MonitoringSeverity::Critical, cl.calculateSeverity(10000, 7000));

    cl.setNonAlertingThresh(5);
    TestEquals("CheckLimits calculate severity with non-alirting threshold", MonitoringSeverity::None, cl.calculateSeverity(9, 3));

    cl.setWarnThresh(0);
    TestEquals("CheckLimits calculate severity with custom warning threshold", MonitoringSeverity::Warning, cl.calculateSeverity(10000, 70));

    TestEquals("CheckLimits equals itself", cl, cl);

    DorBluPB::MonitoringCheckLimits pbCheckLimits;
    cl.serializeTo(&pbCheckLimits);
    auto deserialized = CheckLimits(pbCheckLimits);

    TestEquals("CheckLimits serialization/deserialization", cl, deserialized);
}

TEST(Monitoring, CheckStatTest)
{
    CheckLimits cl;
    CheckStat cs;

    cs.decideSeverity(cl);
    TestEquals("CheckStat initial total",        static_cast<uint64_t>(0), cs.total());
    TestEquals("CheckStat initial bad",          static_cast<uint64_t>(0), cs.bad());
    TestEquals("CheckStat calculate severity 1", MonitoringSeverity::None, cs.severity());

    for (int i = 0; i < 50; ++i) {
        if (i % 2)
            cs.addBad();
        else
            cs.addGood();
    }

    cs.decideSeverity(cl);
    TestEquals("CheckStat filled total",         static_cast<uint64_t>(50),    cs.total());
    TestEquals("CheckStat filled bad",           static_cast<uint64_t>(25),    cs.bad());
    TestEquals("CheckStat calculate severity 1", MonitoringSeverity::Critical, cs.severity());
}

TEST(Monitoring, CheckFeatureTest)
{
    Tokenizer t("files/basic_log_format2.conf", false);
    std::vector<std::string> inputLines = {
        "example.com \"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.200 \"0.198\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.150 \"0.148\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.500 \"0.498\" -",
        "example.com \"GET /ping HTTP/1.1\" 302 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /bar HTTP/1.1\" 200 0.100 \"0.098\" -",
        "example.com \"GET /bar HTTP/1.1\" 200 0.200 \"0.198\" -",
        "example.com \"GET /bar HTTP/1.1\" 200 0.300 \"0.298\" -"
    };

    CheckFeature cf;

    auto bsonCheckFeature = bson::Object();
    TestNotThrowsException("CheckFeature creation with empty MatchRule", [&cf, &bsonCheckFeature] { cf = CheckFeature(bsonCheckFeature); });

    bsonCheckFeature = bson::object("MatchRule", "11");
    TestThrowsException<DorBluError>("CheckFeature creation with illegal MatchRule", [&cf, &bsonCheckFeature] { cf = CheckFeature(bsonCheckFeature); });

    auto bsonMatchRule = bson::object("type", "Equals", "field", "request_url", "operand", "/ping");
    bsonCheckFeature = bson::object("MatchRule", bsonMatchRule);
    TestNotThrowsException("CheckFeature creation with correct MatchRule", [&cf, &bsonCheckFeature] { cf = CheckFeature(bsonCheckFeature); });

    auto bsonLimits = bson::object("Warn", "123");
    bsonCheckFeature = bson::object("MatchRule", bsonMatchRule, "Limits", bsonLimits);
    TestThrowsException<DorBluError>("CheckFeature creation with illegal Limits", [&cf, &bsonCheckFeature] { cf = CheckFeature(bsonCheckFeature); });

    bsonLimits = bson::object("Warn", 0, "Crit", 101, "NonAlerting", 0);
    bsonCheckFeature = bson::object("MatchRule", bsonMatchRule, "Limits", bsonLimits);
    TestNotThrowsException("CheckFeature creation with correct MatchRule and Limits", [&cf, &bsonCheckFeature] { cf = CheckFeature(bsonCheckFeature); });

    const auto& limits = cf.limits();
    TestEquals("Stuffed CheckFeature limits warn",         static_cast<double>(0),   limits.warnThresh());
    TestEquals("Stuffed CheckFeature limits crit",         static_cast<double>(101), limits.critThresh());
    TestEquals("Stuffed CheckFeature limits non alerting", static_cast<uint64_t>(0), limits.nonAlertingThresh());

    TestNotThrowsException("CheckFeature indexing fields", [&cf, &t] { cf.indexFields(t); });

    for (const auto& line : inputLines) {
        auto res = t.tokenize(line);
        if (!res) {
            throw std::runtime_error("Failed to stuff CheckFeature with lines of data");
        }
        if ((*res)[4].asOptionalInt() == 500)
            cf.match(*res, true);
        else
            cf.match(*res, false);
    }

    const auto& urls = cf.urls();
    TestEquals("CheckFeature's urls amount", static_cast<size_t>(1), urls.size());

    const auto& stats = urls.at("example.com/ping");
    TestEquals("example.com/ping total lines",        static_cast<uint64_t>(7), stats.total());
    TestEquals("example.com/ping bad lines",          static_cast<uint64_t>(1), stats.bad());

    const auto& alertingUrls = cf.getAlertingUrls();
    TestEquals("CheckFeature's alerting urls amount", static_cast<size_t>(1), urls.size());

    const auto& alertingStats = alertingUrls.at("example.com/ping");
    TestEquals("example.com/ping severity",           MonitoringSeverity::Warning, alertingStats.severity());

    TestEquals("CheckFeature equals itself", cf, cf);

    DorBluPB::MonitoringCheckFeature pbCheckFeature;
    cf.serializeTo(&pbCheckFeature);
    auto deserialized = CheckFeature(pbCheckFeature);
    TestEquals("CheckFeature serialization/deserialization", cf, deserialized);
}

TEST(Monitoring, CheckTest)
{
    auto bsonCheck = bson::Object();
    Check check;
    TestThrowsException<DorBluError>("Check with empty data", [&bsonCheck, &check] { check = Check(bsonCheck); });

    bsonCheck = bson::object(
        "name", "vhost-500"
    );
    TestThrowsException<DorBluError>("Check with incomplete data 1", [&bsonCheck, &check] { check = Check(bsonCheck); });

    bsonCheck = bson::object(
        "name", "vhost-500",
        "badnessRule", "111"
    );
    TestThrowsException<DorBluError>("Check with incomplete data 2", [&bsonCheck, &check] { check = Check(bsonCheck); });

    auto bsonBadnessRule = bson::object(
        "type", "And",
        "children", bson::array(
            bson::object("type", "GreaterThan", "field", "status", "operand", "499"),
            bson::object("type", "LessThan",    "field", "status", "operand", "600")
        )
    );
    bsonCheck = bson::object("name", "vhost-500", "badnessRule", bsonBadnessRule);
    TestNotThrowsException("Check with minimal complete data", [&bsonCheck, &check] { check = Check(bsonCheck); });

    auto bsonFeatures = bson::array(
        bson::object(
            "MatchRule", bson::object("type", "Equals", "field", "request_url", "operand", "/ping"),
            "Limits", bson::object("Warn", 0, "Crit", 101, "NonAlerting", 0)
        )
    );
    bsonCheck = bson::object(
        "name", "vhost-500",
        "badnessRule", bsonBadnessRule,
        "features", bsonFeatures
    );
    TestNotThrowsException("Check with features", [&bsonCheck, &check] { check = Check(bsonCheck); });

    bsonCheck = bson::object(
        "name", "vhost-500",
        "badnessRule", bsonBadnessRule,
        "features", bsonFeatures,
        "blacklist", bson::array(
            bson::object("type", "Equals", "field", "request_url", "operand", "/black")
        )
    );
    TestNotThrowsException("Check with features and blacklist", [&bsonCheck, &check] { check = Check(bsonCheck); });

    Tokenizer t("files/basic_log_format2.conf", false);
    std::vector<std::string> inputLines = {
        "example.com \"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.200 \"0.198\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.150 \"0.148\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.500 \"0.498\" -",
        "example.com \"GET /ping HTTP/1.1\" 302 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /bar HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /bar HTTP/1.1\" 500 0.200 \"0.198\" -",
        "example.com \"GET /bar HTTP/1.1\" 500 0.300 \"0.298\" -"
        "example.com \"GET /bar HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /bar HTTP/1.1\" 500 0.200 \"0.198\" -",
        "example.com \"GET /bar HTTP/1.1\" 500 0.300 \"0.298\" -"
        "example.com \"GET /black HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /black HTTP/1.1\" 500 0.200 \"0.198\" -",
        "example.com \"GET /black HTTP/1.1\" 500 0.300 \"0.298\" -"
        "example.com \"GET /black HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /black HTTP/1.1\" 500 0.200 \"0.198\" -",
        "example.com \"GET /black HTTP/1.1\" 500 0.300 \"0.298\" -"
        "example.com \"GET /black HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /black HTTP/1.1\" 500 0.200 \"0.198\" -",
        "example.com \"GET /black HTTP/1.1\" 500 0.300 \"0.298\" -"
        "example.com \"GET /black HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /black HTTP/1.1\" 500 0.200 \"0.198\" -",
        "example.com \"GET /black HTTP/1.1\" 500 0.300 \"0.298\" -"
    };
    check.indexFields(t);

    for (const auto& line : inputLines) {
        check.addLine(*t.tokenize(line));
    }

    auto alertMessage = check.getAlertMessage();
    TestEquals("Alert message", std::string("; example.com/ping: WARN(1/7 [14.29%])"), alertMessage);

    const auto& pingStat = check.findUrl("example.com/ping");
    TestEquals("example.com/ping severity", MonitoringSeverity::Warning, pingStat.severity());

    const auto& barStat = check.findUrl("example.com/bar");
    TestEquals("example.com/bar severity", MonitoringSeverity::None, barStat.severity());

    TestThrowsException<DorBluError>("example.com/black severity", [&check]{ check.findUrl("example.com/black"); });

    TestEquals("Check equals itself", check, check);

    DorBluPB::MonitoringCheck pbCheck;
    check.serializeTo(&pbCheck);
    auto deserialized = Check(pbCheck);
    TestEquals("Check serialization/deserialization", check, deserialized);
}

TEST(Monitoring, MonitoringTest)
{
    auto bsonBadnessRule = bson::object(
        "type", "And",
        "children", bson::array(
            bson::object("type", "GreaterThan", "field", "status", "operand", "499"),
            bson::object("type", "LessThan",    "field", "status", "operand", "600")
        )
    );
    auto bsonCheck = bson::object("badnessRule", bsonBadnessRule);

    Monitoring mon;

    TestThrowsException<DorBluError>("Monitoring with incomplete data",
        [&bsonCheck, &mon] { mon = Monitoring(bsonCheck); });

    bsonCheck = bson::object("vhost500", bson::object("MatchRule", bsonBadnessRule));
    TestNotThrowsException("Monitoring with correct data",
        [&bsonCheck, &mon] { mon = Monitoring(bsonCheck); });

    TestEquals("Monitoring equals itself", mon, mon);

    DorBluPB::Monitoring pbMon;
    mon.serializeTo(&pbMon);
    auto deserialized = Monitoring(pbMon);
    TestEquals("Monitoring serialization/deserialization", mon, deserialized);
}
