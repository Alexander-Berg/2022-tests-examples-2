package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.Arrays;
import java.util.Collection;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.TimeUnit;

import junit.framework.TestCase;
import org.joda.time.DateTime;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.api.monitoringd.MonStatus;

@RunWith(Parameterized.class)
public class BsFlapReducerTest extends TestCase {
    static final long NOW = DateTime.now().getMillis();
    private static final TestHelper helper = new TestHelper();
    private static final MonStatus undef = MonStatus.undef;
    private static final MonStatus good = MonStatus.alive;
    private static final MonStatus bad = MonStatus.dead;
    private static final int cid = (int) helper.getRndCounterId(7);
    private static final int cid2 = (int) helper.getRndCounterId(7);
    private static final String mainDom = "domain.ru";
    private static final String subDom = "sub.domain";
    private static final int tBad = 30;
    private static final int tGood = 0;
    private static final int tCross = 15;
    private static final int tDay = 60 * 24;
    @Parameterized.Parameter
    public String name;
    @Parameterized.Parameter(1)
    public Set<MonitoringState> stateList;
    @Parameterized.Parameter(2)
    public Set<MonitoringState> approvedStates;
    @Parameterized.Parameter(3)
    public Set<MonitoringState> discardedStates;
    private BsFlapReducer flapReducer;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getParameters() {
        return Arrays.asList(
                new Object[][]{
                        // Пустой запуск
                        {
                                "Пустой запуск",
                                states(),
                                states(),
                                states()
                        },
                        // Тесты на случаи когда первым пришел неопределенный статус
                        {
                                "Только Один undef",
                                states(qs(cid, undef, 0)),
                                states(qs(cid, undef, 0)),
                                states()
                        },
                        {
                                "Дубль undef",
                                states(qs(cid, undef, 1), qs(cid, undef, 0)),
                                states(qs(cid, undef, 1)),
                                states()
                        },
                        {
                                "Дубль undef + good[complete]",
                                states(qs(cid, undef, tCross + 3), qs(cid, undef, tCross + 2), qs(cid, good, tCross + 1)),
                                states(qs(cid, undef, tCross + 3), qs(cid, good, tCross + 1)),
                                states()
                        },
                        {
                                "Только undef + Bad[complete]",
                                states(qs(cid, undef, tBad + 2), qs(cid, bad, tBad + 1)),
                                states(qs(cid, undef, tBad + 2), qs(cid, bad, tBad + 1)),
                                states()
                        },
                        {
                                "Только undef + Bad[flaping]",
                                states(qs(cid, undef, tBad + 2), qs(cid, bad, tBad + 1), qs(cid, good, tBad + 0)),
                                states(qs(cid, undef, tBad + 2)),
                                states(qs(cid, bad, tBad + 1), qs(cid, good, tBad + 0))
                        },
                        // Тесты для разный случаев с первым пришедшим плохим статусом
                        {
                                "Только Bad[incomplete]",
                                states(qs(cid, bad, tBad - 5)),
                                states(),
                                states()
                        },
                        {
                                "Только Bad[complete]",
                                states(qs(cid, bad, tBad + 5)),
                                states(qs(cid, bad, tBad + 5)),
                                states()
                        },
                        {
                                "Дубли для Bad[complete]",
                                states(qs(cid, bad, tBad + 5), qs(cid, bad, tBad + 4), qs(cid, bad, tBad + 3)),
                                states(qs(cid, bad, tBad + 5)),
                                states(qs(cid, bad, tBad + 4), qs(cid, bad, tBad + 3))
                        },
                        {
                                "Bad[complete] over window",
                                states(qs(cid, bad, 2 * tBad + 4), qs(cid, bad, tBad + 1)),
                                states(qs(cid, bad, 2 * tBad + 4), qs(cid, bad, tBad + 1)),
                                states()
                        },
                        {
                                "Только Bad[Flap]",
                                states(qs(cid, bad, tBad + 3), qs(cid, good, tBad + 2)),
                                states(),
                                states(qs(cid, bad, tBad + 3), qs(cid, good, tBad + 2))
                        },
                        {
                                "Только Bad[Flap] затем Bad[Complete]",
                                states(qs(cid, bad, tBad + 3), qs(cid, good, tBad + 2), qs(cid, bad, tBad + 1)),
                                states(qs(cid, bad, tBad + 1)),
                                states(qs(cid, bad, tBad + 3), qs(cid, good, tBad + 2))
                        },
                        {
                                "Bad[Complete] затем Bad[Flap]",
                                states(qs(cid, bad, tBad + tCross + 5), qs(cid, bad, tCross + 2), qs(cid, good, tCross + 1)),
                                states(qs(cid, bad, tBad + tCross + 5)),
                                states(qs(cid, bad, tCross + 2), qs(cid, good, tCross + 1))
                        },
                        {
                                "Bad[Complete] затем Good[complete]",
                                states(qs(cid, bad, tBad + tCross + 5), qs(cid, good, tCross + 1)),
                                states(qs(cid, bad, tBad + tCross + 5), qs(cid, good, tCross + 1)),
                                states()
                        },
                        {
                                "Double Bad[Complete] затем Good[complete]",
                                states(qs(cid, bad, tBad + tCross + 5), qs(cid, bad, tCross + 6), qs(cid, good, tCross + 1)),
                                states(qs(cid, bad, tBad + tCross + 5), qs(cid, good, tCross + 1)),
                                states(qs(cid, bad, tCross + 6))
                        },
                        {
                                "Bad[Flaps] затем Bad[incomplete]",
                                states(qs(cid, bad, tBad + 5), qs(cid, good, tCross + 6), qs(cid, bad, tCross + 1)),
                                states(),
                                states(qs(cid, bad, tBad + 5), qs(cid, good, tCross + 6))
                        },
                        {
                                "Bad[Flaps] через Double Good",
                                states(
                                        qs(cid, bad, tBad + 4),
                                        qs(cid, good, tBad + 3),
                                        qs(cid, good, tBad + 2),
                                        qs(cid, bad, tBad + 1)
                                ),
                                states(qs(cid, good, tBad + 2), qs(cid, bad, tBad + 1)),
                                states(qs(cid, bad, tBad + 4), qs(cid, good, tBad + 3))
                        },
                        {
                                "Bad Still Flapping",
                                states(qs(cid, bad, tBad + tCross + 1), qs(cid, good, tCross + 3), qs(cid, bad, tCross + 1)),
                                states(),
                                states(qs(cid, bad, tBad + tCross + 1), qs(cid, good, tCross + 3))
                        },
                        {
                                "Bad over badT, good",
                                states(qs(cid, bad, tBad + tCross + 5), qs(cid, bad, tBad + tCross + 1), qs(cid, good, tCross + 1)),
                                states(qs(cid, bad, tBad + tCross + 5), qs(cid, good, tCross + 1)),
                                states(qs(cid, bad, tBad + tCross + 1)) // t3 not complete
                        },
                        {
                                "Bad Not complete",
                                states(qs(cid, bad, tBad + tCross - 5), qs(cid, good, tBad + tCross - 8), qs(cid, bad, tCross + 1)),
                                states(),
                                states(qs(cid, bad, tBad + tCross - 5), qs(cid, good, tBad + tCross - 8))
                        },
                        // Тест на результат в разных сечтиках
                        {
                                "Разные счетчики",
                                states(qs(cid, bad, tBad + 3), qs(cid2, bad, tBad + 1)),
                                states(qs(cid, bad, tBad + 3), qs(cid2, bad, tBad + 1)),
                                states()
                        },
                        // Тест на сдерживание по интервалу проверки на crossorder
                        {
                                "Проверка на CrossOrder skip",
                                states(qs(cid, good, tCross - 3)),
                                states(),
                                states()
                        },
                        {
                                "Проверка на CrossOrder approve",
                                states(qs(cid, bad, tCross + 3), qs(cid, good, tCross + 2)),
                                states(),
                                states(qs(cid, bad, tCross + 3), qs(cid, good, tCross + 2))
                        },
                        {
                                "Проверка на CrossOrder partial",
                                states(qs(cid, bad, tBad + 1), qs(cid, good, tCross - 2)),
                                states(),
                                states(qs(cid, bad, tBad + 1), qs(cid, good, tCross - 2))
                        },
                        {
                                "Проверка на CrossOrder discarded",
                                states(qs(cid, bad, tCross - 2), qs(cid, good, tCross - 3)),
                                states(),
                                states(qs(cid, bad, tCross - 2), qs(cid, good, tCross - 3))
                        },
                        //Большой период в прошлое
                        {
                                "Проверка на большом периоде в прошлое",
                                states(qs(cid, good, tDay), qs(cid, bad, tDay - 10), qs(cid, good, tDay - 50)),
                                states(qs(cid, good, tDay), qs(cid, bad, tDay - 10), qs(cid, good, tDay - 50)),
                                states()
                        },
                        {
                                "Проверка DISCARD на большом периоде",
                                states(qs(cid, good, tDay * 3), qs(cid, bad, tDay * 3 - 10), qs(cid, good, tDay * 3 - 20)),
                                states(qs(cid, good, tDay * 3)),
                                states(qs(cid, bad, tDay * 3 - 10), qs(cid, good, tDay * 3 - 20))
                        },
                        //возврат на краю окна
                        {
                                "Возврат на краю окна",
                                states(qs(cid, bad, tBad + 5), qs(cid, good, 5)),
                                states(),
                                states(qs(cid, bad, tBad + tCross / 3), qs(cid, good, tCross / 3))
                        },
                        //Разный домен на одном счетчике
                        {
                                "Разный домен на счетчике",
                                states(qs(mainDom, bad, tBad + 2), qs(subDom, good, tBad + 1)),
                                states(qs(mainDom, bad, tBad + 2), qs(subDom, good, tBad + 1)),
                                states()
                        }
                });
    }

    private static MonitoringState qs(int counterId, String domain, MonStatus state, int t) {
        return new MonitoringState(
                "dump_message",
                state == MonStatus.alive ? 200 : 500,
                state,
                domain,
                counterId,
                NOW - TimeUnit.MINUTES.toMillis(t)
        ) {
            @Override
            public String toString() {
                return counterId + "[" + domain + "](" + state.toString() + ":" + t + ")";
            }
        };
    }

    private static MonitoringState qs(int counterId, MonStatus state, int t) {
        return qs(counterId, mainDom, state, t);
    }

    private static MonitoringState qs(String domain, MonStatus state, int t) {
        return qs(cid, domain, state, t);
    }

    private static Set<MonitoringState> states(MonitoringState... states) {
        return new HashSet<>(Arrays.asList(states));
    }

    @Before
    public void setUp() throws Exception {

        flapReducer = new BsFlapReducer(tBad, tGood, tCross);
        flapReducer.setNow(NOW);
    }

    @After
    public void tearDown() throws Exception {
        flapReducer = null;
    }

    @Test
    public void processStatesApproved() {
        flapReducer.setNow(NOW);
        flapReducer.processStates(stateList);
        assertEquals(approvedStates, flapReducer.getApproved());
    }

    @Test
    public void processStatesDiscarded() {
        flapReducer.setNow(NOW);
        flapReducer.processStates(stateList);
        assertEquals(discardedStates, flapReducer.getDiscarded());
    }
}
