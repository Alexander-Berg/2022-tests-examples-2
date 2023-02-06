package ru.yandex.metrika.internalapid.direct.external;

import org.junit.Test;

import ru.yandex.metrika.api.management.client.external.goals.GoalStatus;

import static org.junit.Assert.assertEquals;

public class DirectGoalStatusTest {

    @Test
    public void checkGoalStatusMapping() {
        assertEquals(GoalStatus.values().length, DirectGoalStatus.getMapFromGoalRealStatusToDirectStatus().keySet().size());
    }
}
