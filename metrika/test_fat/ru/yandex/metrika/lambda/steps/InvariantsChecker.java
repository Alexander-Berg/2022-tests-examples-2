package ru.yandex.metrika.lambda.steps;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.qameta.allure.Allure;
import io.qameta.allure.Step;
import org.junit.Assert;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import ru.yandex.inside.yt.kosher.tables.YTableEntryTypes;
import ru.yandex.metrika.util.StringUtil;

import static ru.yandex.metrika.lambda.steps.FreemarkerUtils.renderTemplate;

@Component
public class InvariantsChecker {

    private static final Logger log = LoggerFactory.getLogger(InvariantsChecker.class);

    public static final String INVARIANT_ROOT = "//home/metrika-lambda/testing/invariants";

    @Autowired
    private YtFactory ytFactory;

    @Autowired
    @Qualifier("hahnJdbcTemplateV1")
    private JdbcTemplate yqlV1Template;

    private ImmutableList.Builder<Invariant> builder = ImmutableList.builder();

    @Step("Проверить инвариант {invariant.scriptName} ({invariant.version})")
    private InvariantResult performInvariantEvaluation(Invariant invariant) {
        InvariantResult.Builder builder = InvariantResult.builder()
                .withName(invariant.getScriptName())
                .withVersion(invariant.getVersion());

        try (LogMonitor logMonitor = new LogMonitor("Консольный лог")) {
            final String yqlScript = StringUtil.substitute2(invariant.getScriptTemplate(),
                    "invariantRoot", INVARIANT_ROOT,
                    "name", invariant.getTableName());

            builder.withScript(yqlScript);

            if (invariant.getVersion().equals("v1")) {
                yqlV1Template.execute(yqlScript);
            } else {
                throw new RuntimeException(String.format("Unsupported YQL version '%s'", invariant.getVersion()));
            }

            //скрипт выполнился без ошибки, смотрим количество строк в выходной таблице.
            //если её не сущестует - будет брошено исключение, что означает, что результат не был получен
            long row_count = ytFactory.getYt().cypress().get(invariant.getTable().attribute("row_count")).longValue();

            if (row_count != 0) {
                //в таблице есть строки - инвариант не выполнен
                builder.withResult(false)
                        .withDetails(retrieveDetails(invariant));
            } else {
                //в таблице строк нет - инвариант выполнен
                builder.withResult(true);
            }
        } catch (Exception e) {
            //Ошибка при выполнении скрипта - результат не получен
            builder.withError(e);
        }

        return builder.build();
    }

    private List<Map<String, String>> retrieveDetails(Invariant invariant) {
        RowMapperColumnsExtractor extractor = new RowMapperColumnsExtractor();
        ytFactory.getYt().tables().read(invariant.getTable(), YTableEntryTypes.YSON, extractor);
        return extractor.getData();
    }

    public void v1(String name) {
        builder.add(new Invariant("v1", name));
    }

    @Step("Проверить инварианты")
    public void checkInvariants() {
        List<InvariantResult> invariantResults =
                builder.build().stream().map(this::performInvariantEvaluation).collect(Collectors.toList());

        reportResults(invariantResults);

        Assert.assertTrue("Инварианты должны быть выполнены",
                invariantResults.stream().allMatch(invariantResult -> invariantResult.getHasResult() && invariantResult.getResult()));

    }

    private void reportResults(List<InvariantResult> invariantResults) {
        log.info("===> Start report invariants");
        for (InvariantResult invariantResult : invariantResults) {
            Allure.step(String.format("%s %s (%s)", invariantResult.getStatus().toString(), invariantResult.getName(), invariantResult.getVersion()),
                    () -> Allure.addAttachment(invariantResult.getName(), "text/html", getResultReport(invariantResult), ".html"));
        }
        log.info("===> Finish report invariants");
    }

    private String getResultReport(InvariantResult result) {
        log.debug("Render report for invariant: {} {}:'{}'", result.getStatus(), result.getVersion(), result.getName());

        return renderTemplate("steps/invariant.html.ftl", ImmutableMap.<String, Object>builder()
                .put("result", result)
                .build());
    }
}
