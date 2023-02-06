package ru.yandex.autotests.metrika.utils;

import org.junit.Test;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.utils.Utils.getDuplicates;

/**
 * Created by konkov on 14.04.2015.
 */
public class DuplicatesTest {

    @Test
    public void checkDuplicatesOfStrings() {
        List<String> data = asList("A", "B", "A");

        Collection<String> dups = getDuplicates(data);

        assertThat(dups, equalTo(asList("A")));
    }

    @Test
    public void checkDuplicatesOfLists() {
        List<List<String>> data = asList(
                asList("A", "A"),
                asList("A", "B"),
                asList("A", "A")
        );

        Collection<List<String>> dups = getDuplicates(data);

        assertThat(dups, equalTo(asList(asList("A", "A"))));
    }
}
