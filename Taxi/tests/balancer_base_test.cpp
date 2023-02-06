#include <elastic/servers.hpp>

#include <token_vendor.hpp>

#include <boost/utility/base_from_member.hpp>

#include <atomic>

#include <userver/engine/task/task.hpp>
#include <userver/utest/http_client.hpp>
#include <userver/utest/simple_server.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/async.hpp>

namespace {

using namespace pilorama;

struct TestServers final
    : public ::boost::base_from_member<TokenVendor>,  // workaround
      public elastic::Servers {
 public:
  TestServers(const OutputConfig& output, clients::http::Client& http,
              Statistics& statistics, utils::BytesPerSecond limit = {})
      : base_from_member(output.hosts.size(), limit),
        elastic::Servers(output, http, statistics, base_from_member::member) {}
  ~TestServers() = default;

  OnResponseAction OnResponse(HttpResponse response,
                              HttpRequest request) override {
    ++on_response_count;
    EXPECT_EQ(response->body(), request->GetData());
    return OnResponseAction::OK;
  }

  std::atomic<int> on_response_count{0};
};

struct TestSetup {
  OutputConfig conf;

  const std::shared_ptr<clients::http::Client> http_client_ptr =
      utest::CreateHttpClient();
  Statistics stats{0};

  TestServers servers{conf, *http_client_ptr, stats};

  TestSetup(std::initializer_list<std::string> urls)
      : conf{"", "index", "error_index", urls} {}

  explicit TestSetup(utils::BytesPerSecond limit_transmission,
                     std::initializer_list<std::string> urls)
      : conf{"", "index", "error_index", urls},
        servers(conf, *http_client_ptr, stats, limit_transmission) {}
};

static utest::SimpleServer::Response echo_callback(const std::string& request) {
  std::string response = "HTTP/1.1 200 OK\r\nConnection: close\r\r";
  auto payload = request.substr(request.find("\r\n\r\n") + 4);

  response += "Content-Length: " + std::to_string(payload.size());
  response += "\r\n\r\n" + payload;

  return {std::move(response), utest::SimpleServer::Response::kWriteAndClose};
}

}  // namespace

UTEST(BalancerBase, ConstructDestroy) {
  TestSetup t{"invalid_address"};
  EXPECT_EQ(t.servers.on_response_count, 0);
}

UTEST(BalancerBase, TwoTikets) {
  utest::SimpleServer http_server{echo_callback};
  utest::SimpleServer http_server2{echo_callback};
  TestSetup t{http_server.GetBaseUrl(), http_server2.GetBaseUrl()};
  auto ticket1 = t.servers.AcquireRequest(0);
  auto ticket2 = t.servers.AcquireRequest(0);
  EXPECT_EQ(t.servers.on_response_count, 0);

  t.servers.Send("Hello", std::move(ticket2));
  EXPECT_EQ(t.servers.on_response_count, 1);

  t.servers.Send("Word", std::move(ticket1));
  EXPECT_EQ(t.servers.on_response_count, 2);
}

UTEST(BalancerBase, Limittransmission) {
  utest::SimpleServer http_server{echo_callback};
  utest::SimpleServer http_server2{echo_callback};
  constexpr char kData[] = "Some data";
  TestSetup t{utils::BytesPerSecond{1},
              {http_server.GetBaseUrl(), http_server2.GetBaseUrl()}};
  EXPECT_EQ(t.servers.on_response_count, 0);

  auto ticket = t.servers.AcquireRequest(sizeof(kData));
  t.servers.Send(kData, std::move(ticket));
  EXPECT_EQ(t.servers.on_response_count, 1);

  auto task = utils::Async("test", [&] {
    ticket = t.servers.AcquireRequest(sizeof(kData));
    FAIL() << "Acquired ticket while there should be no transmission for the "
              "next `sizeof(kData) - 1` seconds";
  });

  task.WaitFor(std::chrono::seconds(1));
  EXPECT_FALSE(task.IsFinished());
  EXPECT_EQ(t.servers.on_response_count, 1);
}

UTEST(BalancerBase, Balancing) {
  std::atomic<int> first_server_called{0};
  utest::SimpleServer http_server1{[&](const auto& in) {
    ++first_server_called;
    return echo_callback(in);
  }};

  std::atomic<int> second_server_called{0};
  utest::SimpleServer http_server2{[&](const auto& in) {
    ++second_server_called;
    return echo_callback(in);
  }};

  TestSetup t{http_server1.GetBaseUrl(), http_server2.GetBaseUrl()};
  for (unsigned i = 1; i < 10; ++i) {
    auto ticket = t.servers.AcquireRequest(sizeof("Hello"));
    t.servers.Send("Hello", std::move(ticket));

    ticket = t.servers.AcquireRequest(sizeof("test"));
    t.servers.Send("test", std::move(ticket));

    EXPECT_EQ(t.servers.on_response_count, i * 2);
    EXPECT_EQ(first_server_called, i);
    EXPECT_EQ(second_server_called, i);
  }
}

UTEST_MT(BalancerBase, BalancingTortureMT, 4) {
  const unsigned count = 100;
  const unsigned tasks_count = 4;

  std::atomic<int> first_server_called{0};
  utest::SimpleServer http_server1{[&](const auto& in) {
    ++first_server_called;
    return echo_callback(in);
  }};

  std::atomic<int> second_server_called{0};
  utest::SimpleServer http_server2{[&](const auto& in) {
    ++second_server_called;
    return echo_callback(in);
  }};

  TestSetup t{http_server1.GetBaseUrl(), http_server2.GetBaseUrl()};

  auto sends = [&]() {
    for (unsigned i = 0; i < count; ++i) {
      auto ticket = t.servers.AcquireRequest(sizeof("Hello"));
      t.servers.Send("Hello", std::move(ticket));
    }
  };

  engine::Task tasks[tasks_count] = {
      ::utils::Async("sends", sends), ::utils::Async("sends", sends),
      ::utils::Async("sends", sends), ::utils::Async("sends", sends)};

  for (auto& t : tasks) {
    t.WaitFor(utest::kMaxTestWaitTime);
    EXPECT_TRUE(t.IsFinished());
  }

  EXPECT_EQ(t.servers.on_response_count, count * tasks_count);
  EXPECT_EQ(first_server_called, count * tasks_count / 2);
  EXPECT_EQ(second_server_called, count * tasks_count / 2);
}
