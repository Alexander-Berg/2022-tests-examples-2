#pragma once

#include <iostream>
#include <thread>
#include <chrono>
#include <tuple>

#include <library/cpp/testing/gtest/gtest.h>
#include <library/cpp/testing/common/network.h>

#include <taxi/tools/dorblu/lib/include/host.h>
#include <taxi/tools/dorblu/lib/include/tokenizer.h>
#include <taxi/tools/dorblu/lib/include/connection.h>

template <class T>
bool compareValues(const T& expected, const T& got)
{
    if (expected == got) {
        std::cout << "ok." << std::endl;
        return true;
    } else {
        std::cout << "failed." << std::endl;
        std::cout << "Expected: " << expected
                  << " Got: " << got << std::endl;
        return false;
    }
}

void listenForHost(const TSocketHolder& client)
{
    NetworkConnection nc(client);
    auto request = nc.read();

    Tokenizer t("files/basic_log_format2.conf", false);
    Message msg;
    msg.setFromSerialized(request);
    msg.indexFields(t);

    std::vector<std::string> inputLines = {
        "example.com \"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.200 \"0.198\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.150 \"0.148\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 200 0.500 \"0.498\" -",
        "example.com \"GET /ping HTTP/1.1\" 302 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /ping HTTP/1.1\" 500 0.100 \"0.098\" -",
        "example.com \"GET /bar HTTP/1.1\" 200 0.100 \"0.098\" -",
        "example.com \"GET /bar HTTP/1.1\" 200 0.200 \"0.198\" -",
        "example.com \"GET /bar HTTP/1.1\" 200 0.300 \"0.298\" -"
    };

    for (const auto& line : inputLines) {
        auto result = t.tokenize(line);
        EXPECT_TRUE(result);
        msg.match(*result);
    }

    msg.processMonitoring();

    std::string &serialized = msg.getSerialized();
    nc.write(serialized);
}

Host getHost(int port, const char* ruleName = "myRule")
{
    auto bsonFilter = bson::object("type", "StartsWith", "field", "request_url", "operand", "/ping");
    auto bsonRule = bson::object("name", ruleName, "filter", bsonFilter);
    auto rulesArray = bson::array(bsonRule);

    Host host("localhost", rulesArray, port);

    async::Task task(
        [&host, port] {
            async::Listener listener(
                TNetworkAddress("localhost", port),
                listenForHost,
                [] () { std::cerr << "Error while listening" << std::endl; });

            host.run();
            host.wait();
        });
    async::run();

    return host;
}
