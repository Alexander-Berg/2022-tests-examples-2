package com.yandex.launcher.updaterapp;

import com.yandex.launcher.updaterapp.contract.models.Update;

import org.junit.Assert;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

public class CheckResponseTest {

    @Test
    public void createSuccess() {
        final Update oldUpdate = new Update("app1", "a", "", "1.0", 1);
        final Update newUpdate = new Update("app1", "b", "", "MAX_VALUE", Integer.MAX_VALUE);

        final List<Update> updates = new ArrayList<>();
        updates.add(oldUpdate);
        updates.add(newUpdate);

        final List<Update> sortedUpdates = new ArrayList<>();
        sortedUpdates.add(newUpdate);
        sortedUpdates.add(oldUpdate);

        final CheckResponse response = CheckResponse.createSuccessResponse(updates);
        Assert.assertTrue(response.isSuccess());
        Assert.assertEquals(sortedUpdates, response.getUpdates());
    }

    @Test
    public void createError() {
        final String errorMessage = "xxx";
        final CheckResponse response = CheckResponse.createErrorResponse(errorMessage);
        Assert.assertFalse(response.isSuccess());
        Assert.assertEquals(errorMessage, response.getError());
    }
}
