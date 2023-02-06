package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.Arrays;
import java.util.Collection;

import junit.framework.TestCase;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.dbclients.clickhouse.ClickhouseLogEntry;

@RunWith(Parameterized.class)
public class CircularLoggingTaskTest extends TestCase {
    @Parameterized.Parameter
    public String name;
    @Parameterized.Parameter(1)
    public boolean[] returnValues;
    @Parameterized.Parameter(2)
    public int callCount;
    @Parameterized.Parameter(3)
    public int exitByTimeCall;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getParameters() {
        return Arrays.asList(
                new Object[][]{
                        {"Сразу выход", new boolean[]{true}, 1, 4},
                        {"один круг", new boolean[]{false, true}, 2, 4},
                        {"два круга", new boolean[]{false, false, true}, 3, 4},
                        {"два выхода", new boolean[]{false, true, true}, 2, 4},
                        {"Выход по времени", new boolean[]{false, false, false, true}, 2, 2},
                }
        );
    }

    @Test
    public void checkExitByResultValue() throws Exception {
        TaskInstance instance = new TaskInstance(returnValues, exitByTimeCall);
        instance.execute();
        assertEquals(callCount, instance.getCallsCount());
    }

    static class TaskInstance extends CircularLoggingTask<Void, ClickhouseLogEntry> {

        int callsCount = 0;
        int exitByTimeCall;
        boolean[] returnValues;

        public TaskInstance(boolean[] returnValues, int exitByTimeCall) {
            this.returnValues = returnValues;
            this.exitByTimeCall = exitByTimeCall;
        }

        @Override
        boolean executeInnerLoop() throws Exception {
            if (exitByTimeCall == callsCount) {
                setMaxExecutionTimeMinutes(0);
                return false;
            }

            boolean value = returnValues[callsCount];
            callsCount += 1;
            return value;
        }

        public boolean[] getReturnValues() {
            return returnValues;
        }

        public int getCallsCount() {
            return callsCount;
        }
    }

}
