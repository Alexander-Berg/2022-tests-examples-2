package ru.yandex.autotests.tabcrunch.util;

import org.junit.Test;

import java.util.List;

import static org.junit.Assert.assertFalse;
import static ru.yandex.autotests.tabcrunch.util.UniqEmptyList.uniqEmptyList;

/**
 * Created by konkov on 21.09.2016.
 */
public class UniqEmptyListTest {

    @Test
    public void compareTwoInstances() {
        List<String> instance1 = uniqEmptyList();
        List<String> instance2 = uniqEmptyList();

        assertFalse(instance1.equals(instance2));
    }

    @Test
    public void compareSelf() {
        List<String> instance = uniqEmptyList();

        assertFalse(instance.equals(instance));
    }
}
