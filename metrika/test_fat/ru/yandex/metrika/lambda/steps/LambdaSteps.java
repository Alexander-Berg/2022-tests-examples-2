package ru.yandex.metrika.lambda.steps;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.qameta.allure.Allure;
import io.qameta.allure.Attachment;
import io.qameta.allure.Step;
import org.junit.Assert;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import ru.yandex.inside.yt.kosher.cypress.Cypress;
import ru.yandex.inside.yt.kosher.cypress.CypressNodeType;
import ru.yandex.inside.yt.kosher.cypress.YPath;
import ru.yandex.inside.yt.kosher.ytree.YTreeStringNode;
import ru.yandex.metrika.lambda.LambdaOpStat;
import ru.yandex.metrika.lambda.YtChunks;
import ru.yandex.metrika.lambda.steps.bazinga.SelfService;
import ru.yandex.metrika.lambda.task.MetrikaLambdaConfig;
import ru.yandex.metrika.task.LoggingTask;

import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.lessThan;
import static ru.yandex.metrika.lambda.steps.FreemarkerUtils.renderTemplate;

@Component
public class LambdaSteps {

    private static final Logger log = LoggerFactory.getLogger(LambdaSteps.class);

    private static final int MAX_ITERATIONS = 20;

    @Autowired
    private MetrikaLambdaConfig settings;

    @Autowired
    private Map<String, YtChunks> ytChunks;

    @Autowired
    private Map<String, LoggingTask<?, ?>> tasks;

    @Autowired
    private LambdaOpStat lambdaOpStat;

    @Autowired
    private YtFactory ytFactory;

    @Autowired
    private CypressCanonizer cypressCanonizer;

    @Autowired
    private SelfService selfService;

    @Autowired
    @Qualifier("convTemplate")
    private JdbcTemplate convJdbcTemplate;

    @Autowired
    private InvariantsChecker invariantsChecker;

    /**
     * Конфигурирование yt
     */
    @Step("Сконфигурировать YT")
    public void configureYt() {
        // разрешаем bulk insert в динамические таблицы
        getCypress().set(YPath.simple("//sys/@config/tablet_manager/enable_bulk_insert"), true);
        getCypress().set(YPath.simple("//sys/users/root/@enable_bulk_insert"), true);

        // Тут создаются директории, в которые пишут таски, обрабатывающие таблички в несколько потоков.
        // Это начало создавать проблемы после добавления транзакций во все yql запросы, т.к. один из запросов
        // создает директорию, а остальные начинают падать, потому что директория залочена.
        // Поэтому создадим директории заранее
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/dsp_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/dsp_log_filtered"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/adfox_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/adfox_log_filtered"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/adfox_dsp_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/adfox_dsp_log_filtered"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/adfox_yan_log_aggregated"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/adfox_no_yan_log_aggregated"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/adfox_undo_dsp_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/adfox_undo_dsp_log_filtered"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/cdp_order_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/offline_conversion_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/offline_conversion_log_clientid"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/offline_conversion_log_yclid"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/offline_conversion_log_userid"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/recommendation_widget_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/calltracking_crypta_joined_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/calltracking_crypta_joined_log_crypta_id"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/calltracking_crypta_joined_log_direct_client_id"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/calltracking_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/pbx_crypta_joined_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/pbx_crypta_joined_log_crypta_id"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/pbx_crypta_joined_log_extended_user_id"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/pbx_log"), CypressNodeType.MAP);
        getCypress().create(YPath.simple("//home/metrika-lambda/testing/lambda/processing"), CypressNodeType.MAP);
    }

    /**
     * Конфигурирование mysql
     */
    @Step("Сконфигурировать MySQL")
    public void configureMysql() {
        convJdbcTemplate.execute("" +
                "CREATE TABLE IF NOT EXISTS `conversion_lambda_metadata_update_queue` (\n" +
                "  `item_id` int(10) unsigned NOT NULL AUTO_INCREMENT,\n" +
                "  `chunk_id` varchar(64) NOT NULL,\n" +
                "  `log_type` varchar(4) NOT NULL DEFAULT '',\n" +
                "  `uploading_id` int(10) unsigned NOT NULL,\n" +
                "  `uploading_type` int(10) unsigned NOT NULL,\n" +
                "  `line_quantity` int(11) NOT NULL,\n" +
                "  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,\n" +
                "  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\n" +
                "  `is_processed` tinyint(1) DEFAULT '0',\n" +
                "  PRIMARY KEY (`item_id`),\n" +
                "  UNIQUE KEY `chunk_id` (`chunk_id`,`log_type`,`uploading_id`,`uploading_type`),\n" +
                "  KEY `is_processed` (`is_processed`)\n" +
                ") ENGINE=InnoDB DEFAULT CHARSET=utf8"
        );
    }

    /**
     * Тестовый сценарий
     */
    @Step("Сценарий")
    public void performScenario() {
        log.debug(settings.toString());
        log.debug("Chunk types:\n{}", ytChunks.keySet().stream().collect(joining("\n")));
        log.debug("Tasks:\n{}", tasks.entrySet().stream().map(e -> String.format("%s : %s", e.getKey(),
                e.getValue().isEnabled())).collect(joining("\n")));
        dumpCypress();
        //Тут сценарий
        int iteration = 0;
        List<YtChunks.TableInfo> prevState;
        List<YtChunks.TableInfo> currentState = getChunksState();
        reportChunks();
        do {
            iteration++;
            prevState = currentState;
            currentState = Allure.step(String.format("Итерация %d из %d", iteration, MAX_ITERATIONS), () -> {
                executeTasksOnce();
                selfService.executeScheduledTasks();
                List<YtChunks.TableInfo> currentStateInner = getChunksState();
                reportChunks();
                return currentStateInner;
            });
            Assert.assertThat("Chunks processing has not been converged", iteration, lessThan(MAX_ITERATIONS));
        }
        while (hasChanges(prevState, currentState));
        log.info("Chunks processing has been converged");
        reportChunks();
        dumpCypress();
        dumpLambdaOpStat();
    }

    @Step("Дамп чанков")
    private void reportChunks() {
        for (Map.Entry<String, YtChunks> entry : ytChunks.entrySet()) {
            reportChunks(entry.getKey(), entry.getValue().dump());
        }
    }

    @Attachment(value = "{name}", type = "text/html", fileExtension = ".html")
    private String reportChunks(String name, List<Map<String, Object>> rows) {
        return renderTemplate("steps/chunks.html.ftl", ImmutableMap.<String, Object>builder()
                .put("name", name)
                .put("rows", rows)
                .build());
    }

    /**
     * Канонизация выходных данных.
     * <p>
     * Выходные таблицы описывать тут.
     */
    @Step("Канонизация")
    public void canonizeOutput() {

        final List<String> groupColumns = ImmutableList.of("CounterID", "UserID", "VisitID", "VisitVersion", "Sign");

        cypressCanonizer.postprocess(
                YPath.cypressRoot().child("home/metrika-lambda/testing/lambda/out_visits_giga"),
                YPath.cypressRoot().child("postprocess/out_visits_giga"),
                groupColumns);

        cypressCanonizer.path(YPath.cypressRoot().child("postprocess/out_visits_giga"))
                .groupColumns(groupColumns);

        cypressCanonizer.canonizeWithMeta();
    }

    /**
     * Проверка инвариантов.
     * <p>
     * Инварианты описывать тут.
     */
    public void checkInvariants() {
        /* Examples
        invariantsChecker.v1("always_broken.yql");
        invariantsChecker.v1("always_broken2.yql");
        invariantsChecker.v1("always_false.yql");
        invariantsChecker.v1("always_true.yql");
        */

        invariantsChecker.v1("visit_sum_sign.yql");

        invariantsChecker.checkInvariants();
    }

    @Step
    public void dumpCypressState() {
        cypressCanonizer.dumpState();
    }

    private Cypress getCypress() {
        return ytFactory.getYt().cypress();
    }

    private boolean hasChanges(List<YtChunks.TableInfo> prevState, List<YtChunks.TableInfo> currentState) {
        return !prevState.equals(currentState);
    }

    private void executeTasksOnce() {
        for (Map.Entry<String, LoggingTask<?, ?>> entry : tasks.entrySet()) {
            log.info("====> Start executing task {}", entry.getKey());
            if (entry.getValue().isEnabled()) {
                if (entry.getValue().getClass().getPackageName().startsWith("ru.yandex.metrika.lambda")) {
                    Allure.step(entry.getKey(), () -> {
                        try (LogMonitor logMonitor = new LogMonitor("Консольный лог")) {
                            entry.getValue().executeWithLog();
                        }
                    });
                } else {
                    log.info("Task from foreign package. Skip.");
                }
            } else {
                log.info("Task is disabled.");
            }
            log.info("====> Finish executing task {}", entry.getKey());
        }
    }

    private List<YtChunks.TableInfo> getChunksState() {
        return ytChunks.values().stream()
                .map(YtChunks::findAll)
                .flatMap(Collection::stream)
                .sorted(YtChunks.TableInfo.comparingByTypeAndName)
                .collect(toList());
    }

    @Step("Дамп Кипариса")
    private void dumpCypress() {
        Allure.addAttachment("Cypress", "text/plain",
                processFolder(getCypress(), YPath.cypressRoot().child("logs")) + System.lineSeparator() +
                        processFolder(getCypress(), YPath.cypressRoot().child("home")));
    }

    private void dumpLambdaOpStat() {
        Allure.addAttachment("LambdaOpStat", "text/html", renderTemplate("steps/chunks.html.ftl",
                ImmutableMap.<String, Object>builder()
                        .put("name", "LambdaOpStat")
                        .put("rows", lambdaOpStat.dump())
                        .build()), ".html");
    }

    private static String processFolder(Cypress cypress, YPath ypath) {
        log.debug("Processing folder {}", ypath.toString());

        ImmutableList.Builder<String> content = ImmutableList.builder();

        processPath(cypress, ypath, content::add);

        return String.join("\n", content.build());
    }

    private static void processPath(Cypress cypress, YPath ypath, Consumer<String> stringConsumer) {
        String rawType = cypress.get(ypath.attribute("type")).stringValue();
        CypressNodeType nodeType = CypressNodeType.R.fromName(rawType);
        switch (nodeType) {
            case TABLE:
                stringConsumer.accept(processTable(cypress, ypath));
                break;
            case MAP:
                for (YTreeStringNode node : cypress.list(ypath)) {
                    processPath(cypress, ypath.child(node.getValue()), stringConsumer);
                }
                break;
            default:
                log.debug("Ignored '{}' of type '{}'", ypath.toString(), rawType);
        }
    }

    private static String processTable(Cypress cypress, YPath tablePath) {
        Optional<Long> row_count = Optional.empty();
        try {
            if (cypress.exists(tablePath.attribute("row_count"))) {
                row_count = Optional.of(cypress.get(tablePath.attribute("row_count")).longValue());
            }
        } catch (Exception e) {
            log.warn("Error during processing node '{}'\n{}", tablePath.toString(), e.toString());
        }

        return String.format("Table: '%s', rows: %s", tablePath.toString(), row_count.isPresent() ? row_count.get() :
                "N/A");
    }
}
