package ru.yandex.metrika.schedulerd.cron.task.logsapi;

import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.jetbrains.annotations.NotNull;
import org.junit.Assert;
import org.junit.Test;
import org.mockito.Mockito;

import ru.yandex.metrika.api.management.client.external.logs.LogRequest;
import ru.yandex.metrika.api.management.client.external.logs.LogRequestFields;
import ru.yandex.metrika.api.management.client.external.logs.LogsApiDao;
import ru.yandex.metrika.dbclients.AbstractResultSet;
import ru.yandex.metrika.dbclients.mysql.DbUtils;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.managers.GoalIdsDaoImpl;
import ru.yandex.metrika.util.StringUtil;
import ru.yandex.metrika.util.app.XmlPropertyConfigurer;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static java.util.Map.entry;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Array;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.String;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt32;

public class LogsApiTaskTest {

    static LogsApiTask task = new LogsApiTask();
    static TestResultSet testRs = new TestResultSet();
    static List<String> fields = List.of("ym:s:goalsSerialNumber", "ym:s:goalsDateTime",
            "ym:s:goalsPrice", "ym:s:goalsOrder", "ym:s:offlineCallTalkDuration",
            "ym:s:offlineCallHoldDuration", "ym:s:offlineCallMissed",
            "ym:s:offlineCallTag", "ym:s:offlineCallFirstTimeCaller",
            "ym:s:offlineCallURL", "ym:s:goalsID");
    static String activeGoalId = "169482511";


    static {
        LogRequestFields logRequestFields = Mockito.mock(LogRequestFields.class);
        Mockito.when(logRequestFields.getFieldType("ym:s:goalsDateTime")).thenReturn(Array(String()));
        Mockito.when(logRequestFields.getFieldType("ym:s:goalsOrder")).thenReturn(Array(String()));
        Mockito.when(logRequestFields.getFieldType("ym:s:offlineCallTag")).thenReturn(Array(String()));
        Mockito.when(logRequestFields.getFieldType("ym:s:offlineCallURL")).thenReturn(Array(String()));
        Mockito.when(logRequestFields.getFieldType("ym:s:offlineCallURL")).thenReturn(Array(String()));
        Mockito.when(logRequestFields.getFieldType(Mockito.anyString())).thenReturn(Array(UInt32()));
        task.setLogRequestFields(logRequestFields);

        testRs.set(Map.ofEntries(
                entry("ym:s:goalsSerialNumber", "[1,2]"),
                entry("ym:s:goalsDateTime", "['2021-04-15 09:53:27','2021-04-15 10:01:55']"),
                entry("ym:s:goalsPrice", "[0,0]"),
                entry("ym:s:goalsOrder", "['','']"),
                entry("ym:s:offlineCallTalkDuration", "[0,0]"),
                entry("ym:s:offlineCallHoldDuration", "[0,0]"),
                entry("ym:s:offlineCallMissed", "[0,0]"),
                entry("ym:s:offlineCallTag", "['','']"),
                entry("ym:s:offlineCallFirstTimeCaller", "[-1,-1]"),
                entry("ym:s:offlineCallURL", "['','']"),
                entry("ym:s:goalsID", "[155876260,169482511]"))
        );
    }

    @Test
    public void buildRowWithGoalsMetricTest() throws SQLException {
        var goalsFilterSettings = new LogsApiTask.GoalsFilterSettings();
        goalsFilterSettings.activeGoals = Set.of(activeGoalId);
        goalsFilterSettings.needGoalsFiltration = true;
        goalsFilterSettings.goalsIdAdditional = false;

        var result = task.buildRowBytes(testRs, fields, goalsFilterSettings);
        Assert.assertEquals("[2]\t[\\'2021-04-15 10:01:55\\']\t[0]\t[\\'\\']\t[0]\t[0]\t[0]\t[\\'\\']\t[-1]\t[\\'\\']\t[169482511]\n",
                new String(result, StandardCharsets.UTF_8));
    }

    @Test
    public void buildRowWithGoalsMetricWithAdditionalGoalsIdTest() throws SQLException {
        var goalsFilterSettings = new LogsApiTask.GoalsFilterSettings();
        goalsFilterSettings.activeGoals = Set.of(activeGoalId);
        goalsFilterSettings.needGoalsFiltration = true;
        goalsFilterSettings.goalsIdAdditional = true;

        var result = task.buildRowBytes(testRs, fields, goalsFilterSettings);
        Assert.assertEquals("[2]\t[\\'2021-04-15 10:01:55\\']\t[0]\t[\\'\\']\t[0]\t[0]\t[0]\t[\\'\\']\t[-1]\t[\\'\\']\n",
                new String(result, StandardCharsets.UTF_8));
    }

    public static void main(String[] args) throws Exception {
        MySqlJdbcTemplate convmain = convmain();
        LogsApiTask task = new LogsApiTask();
        LogsApiDao dao = new LogsApiDao(convmain);

        task.setLogsApiDao(dao);
        LocaleDictionaries ld = new LocaleDictionaries();
        ld.afterPropertiesSet();
        task.setLocaleDictionaries(ld);

        GoalIdsDaoImpl goalIdsDao=new GoalIdsDaoImpl();
        goalIdsDao.setConvMain(convmain);
        goalIdsDao.afterPropertiesSet();
        task.setGoalIdsDao(goalIdsDao);
        task.init();

        LogRequest request = dao.getLogRequestById(151242);
        task.processRequest(request);
    }

    public static void m4() throws Exception{
        char[] differentChars={'a','\n','\'','\"','\t',' '};
        for (char ch1:differentChars){
            for (char ch2:differentChars){
                for (char ch3:differentChars){
                    for (char ch4:differentChars){
                        String s=""+ch1+ch2+ch3+ch4;
                        String result=StringUtil.escapeTsvDoubleQuotes(s);
                        result=StringUtil.unescapeTsvDoubleQuotes(result);
                        if (!s.equals(result)){
                            throw new Exception("tsv escape/unescape failed");
                        }
                    }
                }
            }
        }
    }

    @NotNull
    private static MySqlJdbcTemplate convmain() {
        return DbUtils.makeJdbcTemplateForTests("localhost", 3312, "metrika", XmlPropertyConfigurer.getTextFromFile("~/.mysql/pass_old"), "conv_main");
    }

    private static class TestResultSet implements AbstractResultSet {
        Map<String, String> data = Map.of();

        void set(Map<String, String> data) {
            this.data = data;
        }

        @Override
        public String getString(String columnLabel) {
            return data.get(columnLabel);
        }
    }

}
