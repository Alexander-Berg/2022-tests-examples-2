package ru.yandex.metrika.schedulerd.cron.task.monitoringd.v2;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertTrue;

@Stories("Monitoring State DAO" )
public class MonitoringStateDaoTest extends MonitoringBaseTest {
    private static final int tHour = 60;
    private static final int tDay = tHour * 24;

    private MonitoringStateDao dao;
    private List<MonitoringState> defaultItems;

    @Before
    public void setUp() throws Exception {
        super.setUp();
        stepsMon.cleanMonitoring(MonitoringStateDao.TABLE);
        dao = new MonitoringStateDao(monitoringTemplate);
        dao.setWaitIntervalHours(1); // = tHour
        dao.setStuckIntervalDays(1); // = tDay
        defaultItems = List.of(
                state(1, UNDEF, 3),
                state(1, BAD, 2),
                state(1, GOOD, 1),
                state(1, BAD, 0)
        );
    }

    @After
    public void tearDown() throws Exception {
        stepsMon.cleanMonitoring(MonitoringStateDao.TABLE);
        dao = null;
        defaultItems = null;
        super.tearDown();
    }

    @Test
    @Title("Проверка вставки новых записей в таблицу" )
    public void insert() {
        long[] insertIds = dao.insert(defaultItems.stream());
        assertNotEquals(insertIds.length, 0);

        List<MonitoringState> stateList = stepsMon.getAll();
        assertTrue(stepsMon.compareMonitoringStates(defaultItems, stateList));

        Set<Long> dbIds = stateList.stream().map(MonitoringState::getId).collect(Collectors.toSet());
        assertEquals(dbIds, Arrays.stream(insertIds).boxed().collect(Collectors.toSet()));
        stepsMon.cleanMonitoring(MonitoringStateDao.TABLE);
    }

    @Test
    @Title("Проверка вставки новых записей в таблицу, с дедупликацией" )
    public void insertDeduplicate() {
        long[] first = dao.insert(defaultItems.stream());
        long[] second = dao.insert(defaultItems.stream());
        List<MonitoringState> stateList = stepsMon.getAll();

        assertNotEquals(first.length, 0);
        assertTrue(stepsMon.compareMonitoringStates(defaultItems, stateList));
        assertArrayEquals(first, second);
    }

    @Test
    @Title("Проверка работы отметки новых записей как прочитанных из логброкера" )
    public void markCommitted() {
        long[] ids = dao.insert(defaultItems.stream());

        dao.markCommited(ids);

        List<MonitoringState> stateList = stepsMon.getAll();
        assertTrue(stepsMon.compareMonitoringStates(defaultItems, stateList));
        assertTrue(stateList.stream().allMatch(MonitoringState::isCommited));
    }

    @Test
    @Title("Проверка отметки записей как обработанных" )
    public void markProcessed() {
        long[] ids = dao.insert(defaultItems.stream());
        dao.markProcessed(Arrays.stream(ids).boxed().collect(Collectors.toList()));

        List<MonitoringState> stateList = stepsMon.getAll();
        assertTrue(stepsMon.compareMonitoringStates(defaultItems, stateList));
        assertTrue(stateList.stream().allMatch(MonitoringState::isProcessed));
    }

    @Test
    @Title("Проверка на правильное задание и проверку по статусу флапа" )
    public void checkFlappingState() {
        List<MonitoringState> items = List.of(
                state(1, UNDEF, 3),
                state(1, BAD, 2),
                state(1, GOOD, 1),
                state(1, BAD, 0)
        );

        items.get(1).setFlappingState(FlappingState.APPROVED);
        items.get(2).setFlappingState(FlappingState.DISCARDED);
        items.get(3).setFlappingState(FlappingState.DISCARDED);

        long[] ids = dao.insert(items.stream());
        List<MonitoringState> flapping = dao.readByFlappingState(FlappingState.FLAPPING);
        assertTrue(stepsMon.compareMonitoringStates(List.of(items.get(0)), flapping));
        List<MonitoringState> approved = dao.readByFlappingState(FlappingState.APPROVED);
        assertTrue(stepsMon.compareMonitoringStates(List.of(items.get(1)), approved));
        List<MonitoringState> discarded = dao.readByFlappingState(FlappingState.DISCARDED);
        assertTrue(stepsMon.compareMonitoringStates(List.of(items.get(2), items.get(3)), discarded));
    }

    @Test
    @Title("Проверка установки статуса флапа по id" )
    public void markFlappingState() {
        List<MonitoringState> items = List.of(
                state(1, UNDEF, 3),
                state(1, BAD, 2),
                state(1, GOOD, 1),
                state(1, BAD, 0)
        );
        long[] ids = dao.insert(items.stream());
        List<MonitoringState> records = dao.readFlapping();
        Set<MonitoringState> toApprove = Set.of(records.get(0), records.get(1));
        Set<MonitoringState> toDiscard = Set.of(records.get(2));
        dao.markFlappingState(
                toApprove,
                toDiscard
        );
        List<MonitoringState> approved = dao.readApproved();
        assertEquals(toApprove, new HashSet<>(approved));

        List<MonitoringState> discarded = dao.readByFlappingState(FlappingState.DISCARDED);
        assertEquals(toDiscard, new HashSet<>(discarded));
    }


    @Test
    @Title("Проверка удаления обработанных или отмененных записей" )
    public void deleteReadyForClean() {

        MonitoringState tooOld = state(1, BAD, tDay * 4);               // can delete by to old range
        MonitoringState undefState = state(1, UNDEF, tHour + 10);   // undef state, in can delete range
        MonitoringState goodState = state(1, GOOD, tHour + 8);      // good state,  in can delete range
        MonitoringState discardedState = state(1, BAD, tHour + 7);  // bad state,   in can delete range
        MonitoringState inSaveRange = state(1, BAD, tHour - 10);    // bad state,   in can delete range


        List<MonitoringState> items = List.of(
                tooOld,
                undefState,
                goodState,
                discardedState,
                inSaveRange
        );

        long[] insertIds = dao.insert(items.stream());
        long tooOldId = insertIds[0];           // not committed, too old (can delete)
        long undefStateId = insertIds[1];       // processed, approved (can delete)
        long goodStateId = insertIds[2];        // processed, approved, not commited (can't delete)
        long discardedStateId = insertIds[3];   // not processed, discarded (can delete)
        long inSaveRangeId = insertIds[4];      // can delete but in save range can't delete)

        dao.markCommited(new long[]{undefStateId, inSaveRangeId, discardedStateId});
        dao.markProcessed(List.of(tooOldId, undefStateId, inSaveRangeId, goodStateId));

        dao.markFlappingState(Set.of(discardedStateId), FlappingState.DISCARDED);
        dao.markFlappingState(Set.of(tooOldId, undefStateId, goodStateId, inSaveRangeId), FlappingState.APPROVED); // Remove only 2, 0 not commited


        dao.deleteReadyForClean();

        List<MonitoringState> stateList = stepsMon.getAll();
        assertEquals(
                Set.of(
                        inSaveRangeId,
                        goodStateId
                ),
                stateList
                        .stream()
                        .map(MonitoringState::getId)
                        .collect(Collectors.toSet())
        );
    }

}
