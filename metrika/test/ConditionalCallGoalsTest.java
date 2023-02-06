package ru.yandex.metrika.lambda.test;

import java.io.IOException;
import java.util.Map;

import org.junit.BeforeClass;
import org.junit.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.StatementCallback;

import ru.yandex.metrika.lambda.YqlDataSourceFactory;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.io.IOUtils;
import ru.yandex.yql.YqlStatement;
import ru.yandex.yql.response.QueryFileDto;
import ru.yandex.yql.settings.YqlProperties;

public class ConditionalCallGoalsTest {

    private static JdbcTemplate yqlTemplate;
    private static String functions;

    @BeforeClass
    public static void init() {
        String yqlHost = System.getenv("YQL_HOST");
        String yqlPort = System.getenv("YQL_PORT");
        String yqlDatabase = System.getenv("YQL_DB");

        YqlDataSourceFactory yqlDataSourceFactory = new YqlDataSourceFactory();
        yqlDataSourceFactory.setUrl("jdbc:yql://" + yqlHost + ":" + yqlPort + "/" + yqlDatabase);
        yqlDataSourceFactory.setYqlProperties(new YqlProperties());

        yqlTemplate = new JdbcTemplate(yqlDataSourceFactory.getYqlDataSource());

        functions = StringUtil.substitute(
                IOUtils.resourceAsString(ConditionalCallGoalsTest.class, "/ru/yandex/metrika/lambda/processing/common/yql/functions.yql"),
                Map.of("cluster", yqlDatabase, "slowVersionMultiplier", 10000)
        );
    }

    @Test
    public void checkConditionCallGoalsReach() {
        execute("conditional_call_goals_reach_test.yql");
    }

    private void execute(String yqlPath) {
        String yql = IOUtils.resourceAsString(ConditionalCallGoalsTest.class, yqlPath);
        yqlTemplate.execute((StatementCallback<Void>) statement -> {
            try {
                YqlStatement yqlStatement = (YqlStatement) statement;
                yqlStatement.attachFile("lambda_functions.sql", QueryFileDto.Type.CONTENT, functions);
                yqlStatement.execute(yql);
                return null;
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
    }
}
