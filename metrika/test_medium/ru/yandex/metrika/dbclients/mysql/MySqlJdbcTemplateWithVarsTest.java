package ru.yandex.metrika.dbclients.mysql;

import java.util.List;

import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;

import ru.yandex.metrika.dbclients.config.JdbcTemplateConfig;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.junit.Assert.assertEquals;

@RunWith(Parameterized.class)
@ContextConfiguration(classes = {MySqlJdbcTemplateWithVarsTest.TestConfig.class})
public class MySqlJdbcTemplateWithVarsTest {

    @ClassRule
    public static final SpringClassRule SCR = new SpringClassRule();
    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    @Autowired
    protected MySqlJdbcTemplate convMainTemplate;
    @Autowired
    TransactionUtil transactionUtil;

    @Parameterized.Parameter()
    public String currentVarName;

    @Parameterized.Parameter(1)
    public int defaultValue;

    @Parameterized.Parameter(2)
    public int tmpValue;

    @Parameterized.Parameters(name = "{0}: {1} -> {2}")
    public static List<Object[]> getParameters() {
        return List.of(
                toArray("@local", 1234, 42),
                toArray("@@SESSION.lock_wait_timeout", 100, 5),
                toArray("@@GLOBAL.key_cache_block_size", 1024, 512)
        );
    }

    @Test
    public void executeWithTemporaryVariable() {
        transactionUtil.doInTransaction(() -> {
            setDefaultValue();
            convMainTemplate.executeWithTemporaryVariable(
                    currentVarName, tmpValue,
                    () -> assertEquals(tmpValue, getVar(convMainTemplate, currentVarName))
            );
            assertEquals(defaultValue, getVar(convMainTemplate, currentVarName));
        });

    }

    private static int getVar(MySqlJdbcTemplate db, String varName) {
        //noinspection ConstantConditions
        return db.queryForObject("SELECT " + varName, Integer.class);
    }

    public void setDefaultValue() {
        convMainTemplate.execute("SET " + currentVarName + " = " + defaultValue);
    }

    @Configuration
    @Import({
            JdbcTemplateConfig.class
    })
    static class TestConfig {
    }
}
