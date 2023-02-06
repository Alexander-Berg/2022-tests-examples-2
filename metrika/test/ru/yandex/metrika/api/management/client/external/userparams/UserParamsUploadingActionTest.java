package ru.yandex.metrika.api.management.client.external.userparams;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * Created by vesel4ak-u on 20.09.16.
 */
public class UserParamsUploadingActionTest {

    @Test
    public void testIsUpdateHeader() {
        assertEquals(true, UserParamsUploadingAction.isUpdateHeader("\tClie  --__ntid "));
    }

    @Test
    public void testIsDeleteHeader() {
        assertEquals(true, UserParamsUploadingAction.isDeleteHeader("\rKEY"));
    }

    @Test
    public void prepareForHeaderCheck1() {
        assertEquals(" aa\\\"\'", UserParamsUploadingAction.prepareForHeaderCheck(" aA\t\\\"\'"));
    }
}
