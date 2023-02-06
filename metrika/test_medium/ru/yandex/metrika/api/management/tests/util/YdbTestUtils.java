package ru.yandex.metrika.api.management.tests.util;

import com.yandex.ydb.table.description.TableDescription;
import com.yandex.ydb.table.settings.CreateTableSettings;
import com.yandex.ydb.table.values.PrimitiveType;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;

public class YdbTestUtils {

    private static final YdbClientProperties ydbClientProperties;

    static {
        ydbClientProperties = new YdbClientProperties();
        ydbClientProperties.setEndpoint(EnvironmentHelper.ydbEndpoint);
        ydbClientProperties.setDatabase(EnvironmentHelper.ydbDatabase);
    }

    public static void createSubscriptionTables() {
        String directoryWithRoot = ydbClientProperties.getDatabase();

        try (YdbSessionManager sessionManager = new YdbSessionManager(ydbClientProperties)) {
            sessionManager.createTable(
                            directoryWithRoot + "/recommendations",
                            TableDescription.newBuilder()
                                    .addNullableColumn("CounterID", PrimitiveType.uint32())
                                    .addNullableColumn("RecommendationId", PrimitiveType.uint32())
                                    .addNullableColumn("Serial", PrimitiveType.uint32())
                                    .addNullableColumn("CreateTime", PrimitiveType.timestamp())
                                    .addNullableColumn("Variables", PrimitiveType.json())
                                    .setPrimaryKeys("CounterID", "RecommendationId", "Serial")
                                    .build(),
                            new CreateTableSettings())
                    .join()
                    .expect("cannot create table recommendations");

            sessionManager.createTable(
                            directoryWithRoot + "/recommendations_create_info",
                            TableDescription.newBuilder()
                                    .addNullableColumn("CounterID", PrimitiveType.uint32())
                                    .addNullableColumn("RecommendationId", PrimitiveType.uint32())
                                    .addNullableColumn("TotalCreate", PrimitiveType.uint32())
                                    .addNullableColumn("TodayCreate", PrimitiveType.uint32())
                                    .addNullableColumn("LastDate", PrimitiveType.date())
                                    .setPrimaryKeys("CounterID", "RecommendationId")
                                    .build(),
                            new CreateTableSettings())
                    .join()
                    .expect("cannot create table recommendations_create_info");

            sessionManager.createTable(
                            directoryWithRoot + "/user_recommendations",
                            TableDescription.newBuilder()
                                    .addNullableColumn("CounterID", PrimitiveType.uint32())
                                    .addNullableColumn("Uid", PrimitiveType.uint64())
                                    .addNullableColumn("RecommendationId", PrimitiveType.uint32())
                                    .addNullableColumn("Serial", PrimitiveType.uint32())
                                    .addNullableColumn("UpdateTime", PrimitiveType.timestamp())
                                    .addNullableColumn("Status", PrimitiveType.utf8())
                                    .setPrimaryKeys("CounterID", "RecommendationId", "Serial")
                                    .build(),
                            new CreateTableSettings())
                    .join()
                    .expect("cannot create table user_recommendations");
        }
    }
}
