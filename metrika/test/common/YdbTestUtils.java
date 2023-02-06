package ru.yandex.metrika.mobmet.crash.decoder.test.common;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import com.yandex.ydb.table.description.TableDescription;
import com.yandex.ydb.table.settings.CreateTableSettings;
import com.yandex.ydb.table.values.PrimitiveType;

import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.async.YdbSchemeManager;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;

public class YdbTestUtils {

    public static YdbClientProperties getTestProperties() {
        return new YdbClientProperties()
                .setEndpoint(readFile("ydb_endpoint.txt"))
                .setDatabase(readFile("ydb_database.txt"));
    }

    public static void createCrashTables() {
        YdbClientProperties properties = getTestProperties();
        String directoryWithRoot = properties.getDatabase() + "/" + "proguard_mappings";
        try (YdbSchemeManager schemeManager = new YdbSchemeManager(properties)) {
            schemeManager.makeDirectory(directoryWithRoot).join().expect("Create directory");
        }
        try (YdbSessionManager sessionManager = new YdbSessionManager(properties)) {
            sessionManager.createTable(
                    directoryWithRoot + "/class_map_compressed",
                    TableDescription.newBuilder()
                            .addNullableColumn("mapping_file_id_hash", PrimitiveType.uint64())
                            .addNullableColumn("mapping_file_id", PrimitiveType.uint64())
                            .addNullableColumn("obfuscated_class_name", PrimitiveType.utf8())
                            .addNullableColumn("original_class_name", PrimitiveType.utf8())
                            .setPrimaryKeys("mapping_file_id_hash", "mapping_file_id", "obfuscated_class_name")
                            .build(),
                    new CreateTableSettings())
                    .join()
                    .expect("cannot create table");

            sessionManager.createTable(
                    directoryWithRoot + "/class_member_map_compressed",
                    TableDescription.newBuilder()
                            .addNullableColumn("mapping_file_id_hash", PrimitiveType.uint64())
                            .addNullableColumn("mapping_file_id", PrimitiveType.uint64())
                            .addNullableColumn("original_class_name", PrimitiveType.utf8())
                            .addNullableColumn("type", PrimitiveType.uint8())
                            .addNullableColumn("member_name", PrimitiveType.utf8())
                            .addNullableColumn("members_info", PrimitiveType.utf8())
                            .setPrimaryKeys(
                                    "mapping_file_id_hash",
                                    "mapping_file_id",
                                    "original_class_name",
                                    "type",
                                    "member_name")
                            .build(),
                    new CreateTableSettings())
                    .join()
                    .expect("cannot create table");
        }
    }

    private static String readFile(String file) {
        try {
            return Files.readString(Paths.get(file));
        } catch (IOException ex) {
            throw new UncheckedIOException(ex);
        }
    }

}
