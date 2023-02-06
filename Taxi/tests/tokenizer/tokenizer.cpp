#include <taxi/tools/dorblu/lib/tests/testbase.h>

#include <iostream>

#include <taxi/tools/dorblu/lib/include/tokenizer.h>

#include <taxi/tools/dorblu/lib/tests/helpers.h>

TEST(Tokenizer, TokenizerFormatTskvTest)
{
    TokenizerFormatTskv format("files/tskv_log_format.conf");

    TestEquals("TokenizerFormatTskv tskv_format boundary",        {"tskv\ttskv_format="},    format.tokenizingBoundaries()[0]);
    TestEquals("TokenizerFormatTskv timestamp boundary",          {"\ttimestamp="},          format.tokenizingBoundaries()[1]);
    TestEquals("TokenizerFormatTskv ssl_handshake_time boundary", {"\tssl_handshake_time="}, format.tokenizingBoundaries()[24]);

    TestEquals("TokenizerFormatTskv tskv_format id",         {0}, format.fields().at("tskv_format"));
    TestEquals("TokenizerFormatTskv timestamp id",           {1}, format.fields().at("timestamp"));
    TestEquals("TokenizerFormatTskv ssl_handshake_time id", {24}, format.fields().at("ssl_handshake_time"));

    /*for (const auto& boundary : format.tokenizingBoundaries()) {
        std::cerr << "<" << boundary << ">" << std::endl;
    }

    for (const auto& field : format.fields()) {
        std::cerr << "<" << field.first << ">: " << field.second << std::endl;
    }*/
}

TEST(Tokenizer, TokenizerFormatNormalTest)
{
    TokenizerFormatNormal format("files/correct_log_format.conf");

    /*for (const auto& boundary : format.tokenizingBoundaries()) {
        std::cerr << "<" << boundary << ">" << std::endl;
    }

    for (const auto& field : format.fields()) {
        std::cerr << "<" << field.first << ">: " << field.second << std::endl;
    }*/
}

TEST(Tokenizer, TokenTest)
{
    Token tString("blah");
    TestEquals("Token(\"blah\") as string", {"blah"}, tString.asStr());
    TestThrowsException<std::invalid_argument>("Token(\"blah\") as int",    [&tString] { tString.asOptionalInt(); });
    TestThrowsException<std::invalid_argument>("Token(\"blah\") as double", [&tString] { tString.asOptionalDouble(); });

    Token tInt("200");
    TestEquals("Token(\"200\") as string", {"200"}, tInt.asStr());
    TestEquals("Token(\"200\") as int",    {200},   tInt.asOptionalInt());
    TestEquals("Token(\"200\") as double", {200},   tInt.asOptionalDouble());

    Token tDouble("1480444998.471");
    TestEquals("Token(\"1480444998.471\") as string", {"1480444998.471"}, tDouble.asStr());
    TestEquals("Token(\"1480444998.471\") as int",    {1480444998},   tDouble.asOptionalInt());
    TestEquals("Token(\"1480444998.471\") as double", {1480444998.471},   tDouble.asOptionalDouble());

    Token tNone("-");
    TestEquals("Token(\"-\") as string", {"-"}, tNone.asStr());
    TestEquals("Token(\"-\") as int", {}, tNone.asOptionalInt());
    TestEquals("Token(\"-\") as double", {}, tNone.asOptionalDouble());
}

TEST(Tokenizer, NormalTokenizerTest)
{
    std::string goodLine = "[30/Nov/2016:02:17:48 +0300] mobile.navi.yandex.net ::ffff:31.173.85.148 \"GET /userpoi/getpoints HTTP/1.1\" 200 \"-\" \"YandexNavigator 104\" \"-\" 0.001 - 1285 \"0.001\" 480 1480461468.403 \"-\" \"-\" \"-\" \"-\" \"-;-;-;-\"";
    std::vector<std::string> badLines = {
        "[30/Nov/2016:02:17:48 +0300] abc 456 mobile.navi.yandex.net ::ffff:31.173.85.148 \"GET /userpoi/getpoints HTTP/1.1\" 200 \"-\" \"-\" 0.001 - 1285 \"0.001\" 480 1480461468.403 \"-\" \"-\" \"-\" \"-\" \"-;-;-;-\"",
        "[30/Nov/2016:02:17:48 +0300] mobile.navi.yandex.net ::ffff:31.173.85.148 \"GET /userpoi/getpoints HTTP/1.1\" 200 \"-\" \"YandexNavigator 104\" \"-\" 0.001 - 1285 \"0.001\" 480 1480461468.403 -\" \"-\" \"-\" \"-\" \"-;-;-;-\"",
        "[30/Nov/2016:02:17:48 +0300] mobile.navi.yandex.net ::ffff:31.173.85.148 \"GET HTTP/1.1\" 200 \"-\" \"YandexNavigator 104\" \"-\" 0.001 - 1285 \"0.001\" 480 1480461468.403 \"-\" \"-\" \"-\" \"-\" \"-;-;-;-\"",
        "[30/Nov/2016:02:17:48 +0300] mobile.navi.yandex.net ::ffff:31.173.85.148 \"GET /userpoi/getpoints HTTP/1.1\" 200 \"-\" \"YandexNavigator 104\" \"-\" 0.001 - 1285 \"0.001\" 480 1480461468.403 \"-\" \"-\" \"-\" \"-\"",
        "[30/Nov/2016:02:17:48 +0300] mobile.navi.yandex.net ::ffff:31.173.85.148 \"GET /userpoi/getpoints HTTP/1.1\" 200 \"-\" \"YandexNavigator 104\" \"-\" 0.001 - 1285 \"0.001\" 480 1480461468.403 \"-\" \"-\" \"-\" \"-\" \"-;-;-;-\" \"+\"",
    };
    TestThrowsException<DorBluError>("Tokenizer(\"files/nonexistantlog_format.conf\")", [] { Tokenizer tokenizer("files/nonexistantlog_format.conf", false); });
    TestThrowsException<DorBluError>("Tokenizer(\"files/empty_log_format.conf\")",      [] { Tokenizer tokenizer("files/empty_log_format.conf", false); });

    Tokenizer tokenizer("files/correct_log_format.conf", false);
    TestEquals("tokenizer[\"time_local\"]",              {0},  tokenizer["time_local"]);
    TestEquals("tokenizer[\"http_X_MegaFon_IMSI\"]",    {23},  tokenizer["http_X_MegaFon_IMSI"]);
    TestEquals("tokenizer[\"status\"]",                  {6},  tokenizer["status"]);
    TestEquals("tokenizer[\"request_url\"]",             {4},  tokenizer["request_url"]);
    TestEquals("tokenizer[\"upstream_response_time\"]", {13},  tokenizer["upstream_response_time"]);
    TestEquals("tokenizer[\"request_time\"]",           {10},  tokenizer["request_time"]);
    TestThrowsException<std::out_of_range>("tokenizer[\"blahfoobar\"]", [&tokenizer] { tokenizer["blahfoobar"]; });

    for (const auto& line : badLines) {
        EXPECT_FALSE(tokenizer.tokenize(line).has_value());
    }

    auto result = *tokenizer.tokenize(goodLine);
    TestEquals("result.size()", {24}, result.size());
    uint32_t status = tokenizer["status"];
    TestEquals("result[\"status\"] as int", {200}, result[status].asOptionalInt());
    uint32_t xMegafonImsi = tokenizer["http_X_MegaFon_IMSI"];
    TestEquals("result[\"http_X_MegaFon_IMSI\"] as str", {"-"}, result[xMegafonImsi].asStr());
}

TEST(Tokenizer, TskvTokenizerTest)
{
    std::string goodLine("tskv\ttskv_format=maps_int\ttimestamp=2017-02-07T14:00:01\ttimezone=+0300\tstatus=200\tprotocol=HTTP/1.0\tmethod=POST\trequest=/wifipool?miid=a9588e39b4e730b7e777a7aa694f4fc715ec83240&uuid=59d4915faf096a476a0252bdf9c300ff&lang=ru_RU&deviceid=b17e87a9ee351bc2f045f1043890df77\treferer=-\tcookies=-\tuser_agent=ru.yandex.yandexnavi/2.32.2321051 mapkit/15.90.45 runtime/44.7.8 android/5.1 (alps; LG-X210; ru_RU)\tvhost=wifipool.maps.yandex.net\tip=2a02:6b8:0:1a10::bf\tx_forwarded_for=::ffff:85.140.6.126\tx_real_ip=::ffff:85.140.6.126\trequest_time=0.051\tupstream_response_time=0.042\tupstream_cache_status=-\tupstream_status=200\tscheme=http\tbytes_sent=202\targs=miid=a9588e39b4e730b7e777a7aa694f4fc715ec83240&uuid=59d4915faf096a476a0252bdf9c300ff&lang=ru_RU&deviceid=b17e87a9ee351bc2f045f1043890df77\tssl_session_id=-\tssl_protocol=-\tssl_cipher=-\tssl_handshake_time=-");

    std::vector<std::string> badLines {
        "[30/Nov/2016:02:17:48 +0300] abc 456 mobile.navi.yandex.net ::ffff:31.173.85.148 \"GET /userpoi/getpoints HTTP/1.1\" 200 \"-\" \"-\" 0.001 - 1285 \"0.001\" 480 1480461468.403 \"-\" \"-\" \"-\" \"-\" \"-;-;-;-\"",
        "tskv\ttskv_format=maps_int\ttimestamp=2017-02-07T14:00:01\ttimezone=+0300\tstatus=200\tprotocol=HTTP/1.0\tmethod=POST\trequest=/wifipool?miid=a9588e39b4e730b7e777a7aa694f4fc715ec83240&uuid=59d4915faf096a476a0252bdf9c300ff&lang=ru_RU&deviceid=    b17e87a9ee351bc2f045f1043890df77\treferer=-\tcookies=-\tuser_agent=ru.yandex.yandexnavi/2.32.2321051 mapkit/15.90.45 runtime/44.7.8 android/5.1 (alps; LG-X210; ru_RU)\tvhost=wifipool.maps.yandex.net\tip=2a02:6b8:0:1a10::bf\tx_forwarded_for=::ffff:85.140.6.126\tx_real_    ip=::ffff:85.140.6.126\trequest_time=0.051\tupstream_response_time=0.042\tupstream_cache_status=-\tupstream_status=200\tscheme=http\tbytes_sent=202\targs=miid=a9588e39b4e730b7e777a7aa694f4fc715ec83240&uuid=59d4915faf096a476a0252bdf9c300ff&lang=ru_RU&deviceid=b17e87a9e    e351bc2f045f1043890df77\tssl_session_id=-\tssl_protocol=-\tssl_cipher=-",
        "123"
    };

    TestThrowsException<DorBluError>("Tokenizer tokenizer(\"files/nonexistantlog_format.conf\")", [] { Tokenizer tokenizer("files/nonexistantlog_format.conf", true); });
    TestThrowsException<DorBluError>("Tokenizer(\"files/basic_log_format.conf\")",      [] { Tokenizer tokenizer("files/basic_log_format.conf", true); });

    Tokenizer tokenizer("files/tskv_log_format.conf", true);

    TestEquals("tskv['tskv_format']", {0}, tokenizer["tskv_format"]);
    TestEquals("tskv['ssl_handshake_time']", {24}, tokenizer["ssl_handshake_time"]);

    for (const auto& line : badLines) {
        EXPECT_FALSE(tokenizer.tokenize(line).has_value());
    }

    auto result = *tokenizer.tokenize(goodLine);
    TestEquals("Tskv result.size()", {25}, result.size());
    uint32_t status = tokenizer["status"];
    TestEquals("Tskv result[\"status\"] as int", {200}, result[status].asOptionalInt());
    uint32_t ssl_handshake_time = tokenizer["ssl_handshake_time"];
    TestEquals("Tskv result[\"ssl_handshake_time\"] as string", {"-"}, result[ssl_handshake_time].asStr());
}
