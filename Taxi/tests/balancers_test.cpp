#include <balancers.hpp>

#include <userver/utest/http_client.hpp>
#include <userver/utest/simple_server.hpp>
#include <userver/utest/utest.hpp>

using namespace pilorama;

UTEST(Balancers, MergeSame) {
  const std::shared_ptr<clients::http::Client> http_client_ptr =
      utest::CreateHttpClient();
  Statistics stats{0};

  ConfigEntry c;
  c.output.hosts = {"host1", "host2", "host3"};
  c.output.max_in_flight_requests = 0;

  std::vector<ConfigEntry> configs = {c, c, c, c};

  Balancers b{configs, *http_client_ptr, stats};

  EXPECT_EQ(b.VendorsCount(), 1);
  for (unsigned i = 1; i < b.Count(); ++i) {
    EXPECT_EQ(&b.At(0), &b.At(i))
        << "Failed to merge same config entries 0 and " << i;
  }
}

UTEST(Balancers, DontMergeDefaultGroupWithLimit) {
  const std::shared_ptr<clients::http::Client> http_client_ptr =
      utest::CreateHttpClient();
  Statistics stats{0};

  ConfigEntry c;
  c.output.hosts = {"host1", "host2", "host3"};
  c.output.max_in_flight_requests = 2;

  std::vector<ConfigEntry> configs = {c, c, c, c};
  Balancers b{configs, *http_client_ptr, stats};

  EXPECT_EQ(b.VendorsCount(), 4);
  for (unsigned i = 1; i < b.Count(); ++i) {
    EXPECT_NE(&b.At(0), &b.At(i)) << "Merge config entries 0 and " << i;
  }
}

UTEST(Balancers, MergeGroupWithLimit) {
  const std::shared_ptr<clients::http::Client> http_client_ptr =
      utest::CreateHttpClient();

  ConfigEntry c;
  c.output.hosts = {"host1", "host2", "host3"};
  c.output.max_in_flight_requests = 2;
  c.output.balancing_group = "group0";

  std::vector<ConfigEntry> configs = {c, c};
  c.output.hosts = {"host17", "host24", "host37"};
  configs.push_back(c);

  Statistics stats{configs.size()};

  Balancers b{configs, *http_client_ptr, stats};

  EXPECT_EQ(b.VendorsCount(), 1);
  EXPECT_EQ(&b.At(0), &b.At(1)) << "Failed to merge config entries 0 and 1";
  EXPECT_NE(&b.At(0), &b.At(2)) << "Merged config entries 0 and 2";
}
