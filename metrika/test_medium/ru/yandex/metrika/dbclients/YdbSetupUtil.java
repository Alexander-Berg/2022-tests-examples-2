package ru.yandex.metrika.dbclients;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import com.yandex.ydb.scheme.SchemeOperationProtos;
import com.yandex.ydb.table.settings.DropTableSettings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.async.YdbSchemeManager;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;

import static com.yandex.ydb.scheme.SchemeOperationProtos.Entry.Type.DIRECTORY;
import static com.yandex.ydb.scheme.SchemeOperationProtos.Entry.Type.TABLE;
import static com.yandex.ydb.table.query.Params.empty;
import static ru.yandex.metrika.dbclients.ydb.YdbMisc.defaultWriteTxControl;

public class YdbSetupUtil {

    private static final Logger log = LoggerFactory.getLogger(YdbSetupUtil.class);
    private static final YdbClientProperties ydbClientProperties;
    private static final YdbSchemeManager ydbSchemeManager;
    private static final YdbSessionManager ydbSessionManager;

    static {
        ydbClientProperties = new YdbClientProperties();
        ydbClientProperties.setEndpoint(EnvironmentHelper.ydbEndpoint);
        ydbClientProperties.setDatabase(EnvironmentHelper.ydbDatabase);

        ydbSchemeManager = new YdbSchemeManager(ydbClientProperties);
        ydbSessionManager = new YdbSessionManager(ydbClientProperties);

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            log.info("Closing ydbSchemeManager and ydbSessionManager");
            ydbSchemeManager.close();
            ydbSessionManager.close();
        }));
    }


    private static final Set<String> settedUpFolders = new HashSet<>();

    public static synchronized void setupYdbFolders(String... folders) {
        setupYdbFolders(Arrays.asList(folders));
    }

    public static synchronized void setupYdbFolders(List<String> folders) {
        var database = EnvironmentHelper.ydbDatabase;

        List<String> existingFolderNames = getChildrenNames(database, DIRECTORY);
        log.info("Existing folders: {}", existingFolderNames);
        for (String folder : folders) {
            if (settedUpFolders.contains(folder)) {
                log.info("Already setted up folder {}. Will skip", folder);
                continue;
            }
            var folderPath = folder.equals("") ? database : database + "/" + folder;
            if (existingFolderNames.contains(folder) || folder.equals("")) {
                log.info("Folder with path {} should be cleaned up", folderPath);
                var tables = getChildrenNames(folderPath, TABLE);
                for (String table : tables) {
                    var tablePath = folderPath + "/" + table;
                    log.info("dropping table with path {}", tablePath);
                    ydbSessionManager.dropTable(tablePath, new DropTableSettings()).join().expect("can not drop table " + tablePath);
                }
            } else {
                log.info("creating folder {}", folderPath);
                createFolder(folderPath);
            }
            settedUpFolders.add(folder);
        }
    }

    public static synchronized void truncateTablesIfExists(String... tablePaths) {
        for (String tablePath : tablePaths) {
            var tablePathPrefix = tablePath.substring(0, tablePath.lastIndexOf('/'));
            var tableName = tablePath.substring(tablePath.lastIndexOf('/') + 1);
            var tables = getChildrenNames(tablePathPrefix, TABLE);
            log.info("Tables in {}: {}", tablePathPrefix, tables);
            var exists = tables.contains(tableName);
            if (exists) {
                // truncate
                var query = "DELETE FROM `" + tablePath + "` WHERE true";
                log.info("Truncating table {}. Executing query: {}", tablePath, query);
                ydbSessionManager.execute(
                        query,
                        empty(),
                        defaultWriteTxControl(),
                        rs -> null
                );
            }
        }
    }

    private static synchronized void createFolder(String folder) {
        ydbSchemeManager.makeDirectory(folder).join().expect("cannot create folder" + folder);
    }

    private static List<String> getChildrenNames(String path, SchemeOperationProtos.Entry.Type type) {
        return ydbSchemeManager.listDirectory(path)
                .join()
                .expect("can not list " + path)
                .getChildren()
                .stream()
                .filter(entry -> entry.getType().equals(type))
                .map(SchemeOperationProtos.Entry::getName)
                .collect(Collectors.toList());
    }

}
