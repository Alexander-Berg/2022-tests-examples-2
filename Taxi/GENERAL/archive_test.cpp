#include <optional>
#include <taxi/graph/tools/taxi-trackstory-archive/internal/impl.hpp>
#include <library/cpp/testing/unittest/env.h>
#include <library/cpp/testing/unittest/registar.h>

Y_UNIT_TEST_SUITE(archive_test) {
    Y_UNIT_TEST(make_mds_key) {
        DriverId driver_id = std::make_pair("dbid", "uuid");
        const auto mds_prefix = "prefix";
        NTaxi::NGraph2::TTimestamp t = 1638341943;
        auto ret = MakeMdsKey(driver_id, t, mds_prefix);

        UNIT_ASSERT_EQUAL(ret, "prefix/dbid/uuid/20211201/6");
    }

    Y_UNIT_TEST(get_date_from_table_name) {
        DriverId driver_id = std::make_pair("dbid", "uuid");
        const auto mds_prefix = "prefix";
        // Tables in moscow time
        NTaxi::NGraph2::TTimestamp t = GetDateFromYtTableName("aaa/aaa//aaa/aaa/aaa/2021-12-01T10:00:00");
        auto ret = MakeMdsKey(driver_id, t, mds_prefix);

        UNIT_ASSERT_EQUAL(ret, "prefix/dbid/uuid/20211201/7");
    }
}
