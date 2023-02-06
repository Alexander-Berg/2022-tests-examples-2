package ru.yandex.metrika.mobmet.crash.decoder.steps;

import com.yandex.ydb.table.description.TableDescription;
import com.yandex.ydb.table.settings.CreateTableSettings;
import com.yandex.ydb.table.values.PrimitiveType;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;

import static java.lang.String.format;

@Component
public class YdbSteps {

    private final YdbTemplate ydbClient;

    public YdbSteps() {
        YdbSessionManager sessionManager = new YdbSessionManager(new YdbClientProperties()
                .setEndpoint(System.getenv("YDB_ENDPOINT"))
                .setDatabase(System.getenv("YDB_DATABASE"))
                .setYdbToken(System.getenv("YDB_TOKEN")));
        this.ydbClient = new YdbTemplate(sessionManager);
    }

    public void createCrashGroupsManagement() {
        createTable(
                "crash_groups/management",
                TableDescription.newBuilder()
                        .addNullableColumn("app_id_hash", PrimitiveType.uint64())
                        .addNullableColumn("app_id", PrimitiveType.uint32())
                        .addNullableColumn("event_type", PrimitiveType.uint8())
                        .addNullableColumn("crash_group_id", PrimitiveType.uint64())
                        .addNullableColumn("comment", PrimitiveType.utf8())
                        .addNullableColumn("status", PrimitiveType.uint8())
                        .addNullableColumn("last_crash_session_date", PrimitiveType.date())
                        .addNullableColumn("last_crash_event_date", PrimitiveType.date())
                        .addNullableColumn("last_crash_processing_time", PrimitiveType.timestamp())
                        .addNullableColumn("create_time", PrimitiveType.timestamp())
                        .addNullableColumn("update_time", PrimitiveType.timestamp())
                        .addNullableColumn("first_crash_session_date", PrimitiveType.date())
                        .addNullableColumn("first_crash_event_date", PrimitiveType.date())
                        .setPrimaryKeys("app_id_hash", "app_id", "event_type", "crash_group_id")
                        .build());
    }

    public void createCrashGroupsAppVersions() {
        createTable(
                "crash_groups/app_versions",
                TableDescription.newBuilder()
                        .addNullableColumn("create_time", PrimitiveType.timestamp())
                        .addNullableColumn("app_id_hash", PrimitiveType.uint64())
                        .addNullableColumn("app_id", PrimitiveType.uint32())
                        .addNullableColumn("event_type", PrimitiveType.uint8())
                        .addNullableColumn("crash_group_id", PrimitiveType.uint64())
                        .addNullableColumn("app_version_name", PrimitiveType.utf8())
                        .addNullableColumn("app_build_number", PrimitiveType.uint32())
                        .setPrimaryKeys(
                                "app_id_hash",
                                "app_id",
                                "event_type",
                                "crash_group_id",
                                "app_version_name",
                                "app_build_number")
                        .build());
    }

    public void createOpenCrashGroupEvents() {
        createTable(
                "crash_groups/open_group_events",
                TableDescription.newBuilder()
                        .addNullableColumn("app_id_hash", PrimitiveType.uint64())
                        .addNullableColumn("app_id", PrimitiveType.uint32())
                        .addNullableColumn("open_time", PrimitiveType.timestamp())
                        .addNullableColumn("event_date", PrimitiveType.date())
                        .addNullableColumn("crash_group_id", PrimitiveType.uint64())
                        .addNullableColumn("crash_group_name", PrimitiveType.utf8())
                        .addNullableColumn("open_type", PrimitiveType.uint8())
                        .addNullableColumn("event_type", PrimitiveType.uint8())
                        .addNullableColumn("operating_system", PrimitiveType.uint8())
                        .addNullableColumn("app_version_name", PrimitiveType.utf8())
                        .addNullableColumn("app_build_number", PrimitiveType.uint32())
                        .setPrimaryKeys("app_id_hash", "app_id", "event_type", "crash_group_id")
                        .build());
    }

    public void createTable(String table, TableDescription description) {
        ydbClient.createTable(ydbClient.getDatabase() + "/" + table, description, new CreateTableSettings())
                .join()
                .expect(format("Failed to create table %s", table));
    }
}
