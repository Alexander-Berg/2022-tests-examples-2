package ru.yandex.autotests.metrika.utils;

import org.hamcrest.Matchers;
import org.junit.Test;

import java.util.LinkedList;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.utils.Utils.flatten;

/**
 * Created by konkov on 16.07.2015.
 */
public class FlattenTest {

    @Test
    public void checkNull() {
        List<String> list = new LinkedList<>();

        list.add(null);

        assertThat(flatten(list), Matchers.<List>equalTo(list));
    }

    @Test
    public void checkNullNull() {
        List<String> list = new LinkedList<>();

        list.add(null);

        List<List<String>> listOfLists = new LinkedList<>();
        listOfLists.add(list);

        assertThat(flatten(listOfLists), Matchers.<List>equalTo(list));
    }
}
