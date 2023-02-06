package ru.yandex.metrika.common.test.medium;

import java.util.List;

import org.joda.time.LocalDateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Component;

import ru.yandex.clickhouse.settings.ClickHouseProperties;
import ru.yandex.metrika.dbclients.clickhouse.ClickHouseSource;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplateImpl;
import ru.yandex.metrika.dbclients.clickhouse.MetrikaClickHouseProperties;
import ru.yandex.metrika.dbclients.clickhouse.SingleTableChunkWriter;
import ru.yandex.metrika.dbclients.mysql.ErrorCountMapper;
import ru.yandex.metrika.dbclients.zookeeper.ZooClient;
import ru.yandex.metrika.util.chunk.ChunkRow;
import ru.yandex.metrika.util.chunk.JsonRecountRequestCodec;
import ru.yandex.metrika.util.chunk.RecountRequest;

import static java.lang.Integer.parseInt;
import static java.lang.String.format;
import static java.util.Collections.singletonList;
import static org.apache.zookeeper.CreateMode.PERSISTENT_SEQUENTIAL;
import static ru.yandex.metrika.dbclients.mysql.RowMappers.STRING;

@Lazy
@Component
public class CalcCloudSteps {

    private static final Logger log = LoggerFactory.getLogger(CalcCloudSteps.class);

    private final String host;

    private final int port;

    @Autowired
    private RandomSteps random;

    @Autowired
    private ZooClient zooClient;

    public CalcCloudSteps() {
        this.host = System.getenv("RECIPE_CLICKHOUSE_HOST");
        this.port = parseInt(System.getenv("RECIPE_CLICKHOUSE_HTTP_PORT"));
    }

    public <T extends ChunkRow> String writeInputChunk(String dataBase, String tablePrefix, String createTableTemplate, String zkPath, List<T> events) {
        String chunkId = random.generateChunkName();
        String tableName = tablePrefix + chunkId;

        writeInputTable(dataBase, tableName, createTableTemplate, events);

        RecountRequest recountRequest = new RecountRequest();
        recountRequest.setChunkId(chunkId);
        recountRequest.setMinTime(LocalDateTime.now());
        recountRequest.setMaxTime(LocalDateTime.now());
        recountRequest.setEventTime(LocalDateTime.now());
        recountRequest.setSize(events.size());
        List<RecountRequest.HostInfo> hostInfos = singletonList(new RecountRequest.HostInfo(host, port, dataBase + '/' + tableName, dataBase, tableName, ""));
        recountRequest.setHostInfos(hostInfos);

        String recountRequestPath = format("%s/recount-request-", zkPath);
        String recountRequestData = new JsonRecountRequestCodec().asText(recountRequest);
        try {
            zooClient.getClient().create().creatingParentsIfNeeded().withMode(PERSISTENT_SEQUENTIAL).forPath(recountRequestPath, recountRequestData.getBytes());
        } catch (Exception exception) {
            log.error("Failed to create ZooKeeper node for recount request.");
            throw new RuntimeException(exception);
        }

        return chunkId;
    }

    public <T extends ChunkRow> void writeInputTable(String dataBase, String tableName, String createTableTemplate, List<T> events) {
        HttpTemplate template = getHttpTemplate(dataBase);
        template.createDatabase();
        template.update(format(createTableTemplate, dataBase, tableName));

        SingleTableChunkWriter<T> chunkWriter = new SingleTableChunkWriter<>(template, tableName);
        chunkWriter.addChunk(events);
        chunkWriter.flush();
    }

    public <T extends ChunkRow> List<T> readOutputChunk(String dataBase, String tableName, ErrorCountMapper<T> rowMapper) {
        return getHttpTemplate(dataBase).query(format("select * from %s", tableName), rowMapper);
    }

    public List<String> listDatabases() {
        return getHttpTemplate("default").query("show databases", STRING);
    }

    public List<String> listTables(String database) {
        return getHttpTemplate(database).query(format("show tables from %s", database), STRING);
    }

    public void recreateDatabase(String database) {
        if (listDatabases().contains(database)) {
            getHttpTemplate(database).update(format("drop database %s", database));
        }
        createDatabase(database);
    }

    public void createDatabase(String database) {
        getHttpTemplate(database).createDatabase();
    }

    private HttpTemplate getHttpTemplate(String dataBase) {
        ClickHouseSource source = new ClickHouseSource(host, port, dataBase);
        ClickHouseProperties properties = new MetrikaClickHouseProperties();
        HttpTemplateImpl template = new HttpTemplateImpl();
        template.setDb(source);
        template.setProperties(properties);
        template.afterPropertiesSet();
        return template;
    }

}
