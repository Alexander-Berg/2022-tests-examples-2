#pragma once

#include <util/system/env.h>

#include <ydb/public/sdk/cpp/client/ydb_driver/driver.h>
#include <ydb/public/sdk/cpp/client/ydb_table/table.h>

#include <taxi/ydb-wrapper/lib/include/client.h>

class TYdbUtilsBase {
public:
    NTaxi::Ydb::Client& GetClient() {
        return *client_;
    }

    NYdb::NTable::TTableClient& GetNativeClient() {
        return *native_client_;
    }

protected:
    void InitializeClients() {
        const auto endpoint = GetEnv("YDB_ENDPOINT");
        const auto database = GetEnv("YDB_DATABASE");

        NTaxi::Ydb::ClientConfig config;
        config.SetEndpoint(endpoint.data()).SetDatabase(database.data());
        client_ = std::make_shared<NTaxi::Ydb::Client>(std::move(config));

        auto native_config = NYdb::TDriverConfig().SetEndpoint(endpoint).SetDatabase(database);
        native_driver_ = std::make_shared<NYdb::TDriver>(native_config);
        native_client_ = std::make_shared<NYdb::NTable::TTableClient>(*native_driver_);
    }

private:
    std::shared_ptr<NTaxi::Ydb::Client> client_;
    std::shared_ptr<NYdb::TDriver> native_driver_;
    std::shared_ptr<NYdb::NTable::TTableClient> native_client_;
};
