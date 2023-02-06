#include <gtest/gtest.h>

#include <memory>

#include <secdist/secdist.hpp>
#include <secdist/settings/archive_api.hpp>
#include <secdist/settings/mds.hpp>
#include <secdist/settings/mongo.hpp>
#include <secdist/settings/postgresql.hpp>
#include <secdist/settings/protocol.hpp>
#include <secdist/settings/redis.hpp>
#include <secdist/settings/storage.hpp>
#include <secdist/settings/tracker.hpp>
#include <secdist/settings/tvm.hpp>
#include <secdist/settings/xiva.hpp>
#include <secdist/settings/yt.hpp>

namespace {
std::shared_ptr<secdist::SecdistConfig> GetSecdist() {
  return std::make_shared<secdist::SecdistConfig>(std::string(SECDIST_PATH));
}
}  // namespace

TEST(SecdistTest, ArchiveApiSettings) {
  secdist::ArchiveApiSettings archive_api =
      GetSecdist()->Get<secdist::ArchiveApiSettings>();

  EXPECT_STREQ("archive_api_token", archive_api.token.c_str());
  ASSERT_FALSE(archive_api.tokens_read.empty());
  ASSERT_FALSE(archive_api.tokens_restore.empty());
}

TEST(SecdistTest, TvmSettings) {
  secdist::TvmSettings common = GetSecdist()->Get<secdist::TvmSettings>();

  ASSERT_FALSE(common.tvm_services.empty());
  ASSERT_FALSE(std::begin(common.tvm_services)->first.empty());
  ASSERT_TRUE(std::begin(common.tvm_services)->second.id);
}

TEST(SecdistTest, YtSecdistSettings) {
  secdist::YtSecdistSettings common =
      GetSecdist()->Get<secdist::YtSecdistSettings>();

  ASSERT_FALSE(common.yt_settings.empty());
  ASSERT_FALSE(std::begin(common.yt_settings)->first.empty());
  ASSERT_FALSE(std::begin(common.yt_settings)->second.prefix.empty());
  ASSERT_FALSE(std::begin(common.yt_settings)->second.api_version.empty());
  ASSERT_FALSE(std::begin(common.yt_settings)->second.proxy_url.empty());
}

TEST(SecdistTest, MdsSettings) {
  secdist::MdsSettings mds = GetSecdist()->Get<secdist::MdsSettings>();

  ASSERT_FALSE(mds.mds_token.empty());
}

TEST(SecdistTest, MongoSettings) {
  secdist::MongoSettings mongo = GetSecdist()->Get<secdist::MongoSettings>();

  ASSERT_FALSE(mongo.GetConnectionString("taxi").empty());
}

TEST(SecdistTest, PsqlConfig) {
  secdist::psql::Config postgresql = GetSecdist()->Get<secdist::psql::Config>();

  ASSERT_TRUE(postgresql.composite_tables_count);
  ASSERT_FALSE(postgresql.databases.empty());

  auto databases = postgresql.databases;
  ASSERT_FALSE(std::begin(databases)->first.empty());
  ASSERT_FALSE(std::begin(databases)->second.empty());

  auto shards = std::begin(databases)->second;
  auto shard = std::begin(shards);
  ASSERT_FALSE(shard->master.connection_string.empty());

  ASSERT_TRUE(postgresql.databases.count("reposition"));
  ASSERT_FALSE(postgresql.databases.at("reposition").empty());
  const auto& reposition = postgresql.databases.at("reposition").front();

  ASSERT_FALSE(reposition.master.connection_string.empty());
  ASSERT_TRUE(reposition.master.preinit_connections);
  ASSERT_EQ(*reposition.master.preinit_connections, 10u);
  ASSERT_FALSE(reposition.sync_slave.preinit_connections);
  ASSERT_FALSE(reposition.slave.preinit_connections);

  const auto& slaves_by_dc = reposition.slaves_by_dc;
  ASSERT_EQ(slaves_by_dc.size(), 3u);
  ASSERT_TRUE(slaves_by_dc.count("vla"));
  ASSERT_FALSE(slaves_by_dc.at("vla").connection_string.empty());
  ASSERT_TRUE(slaves_by_dc.at("vla").preinit_connections);
  ASSERT_EQ(*slaves_by_dc.at("vla").preinit_connections, 4u);

  ASSERT_TRUE(slaves_by_dc.count("myt"));
  ASSERT_FALSE(slaves_by_dc.at("myt").connection_string.empty());
  ASSERT_FALSE(slaves_by_dc.at("myt").preinit_connections);

  ASSERT_TRUE(slaves_by_dc.count("sas"));
  ASSERT_FALSE(slaves_by_dc.at("sas").connection_string.empty());
  ASSERT_FALSE(slaves_by_dc.at("sas").preinit_connections);
}

TEST(SecdistTest, ProtocolSettings) {
  secdist::ProtocolSettings protocol =
      GetSecdist()->Get<secdist::ProtocolSettings>();

  auto billing_service = protocol.GetBillingService("card");
  ASSERT_FALSE(billing_service.name.empty());
  ASSERT_TRUE(billing_service.id);
  ASSERT_FALSE(billing_service.api_key.empty());
}

TEST(SecdistTest, RedisSettings) {
  secdist::RedisMapSettings redis =
      GetSecdist()->Get<secdist::RedisMapSettings>();

  auto settings = redis.GetSettings("taxi-chat");
  ASSERT_FALSE(settings.shards.empty());
  ASSERT_FALSE(settings.sentinels.empty());

  auto host_port = std::begin(settings.sentinels);
  ASSERT_FALSE(host_port->host.empty());
}

TEST(SecdistTest, TrackerSettings) {
  secdist::TrackerSettings tracker =
      GetSecdist()->Get<secdist::TrackerSettings>();

  ASSERT_FALSE(tracker.auto_ru_api_token.empty());
}

TEST(SecdistTest, XivaSettings) {
  secdist::XivaSettings xiva = GetSecdist()->Get<secdist::XivaSettings>();

  ASSERT_FALSE(xiva.sending_token_map.empty());
  ASSERT_FALSE(xiva.subscription_token_map.empty());
}
