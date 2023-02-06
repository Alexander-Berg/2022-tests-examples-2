package ru.yandex.audience.crypta.tasks.uploading;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.Test;

import ru.yandex.metrika.util.collections.CloseableIterator;
import ru.yandex.metrika.util.collections.CloseableIterators;

import static com.google.common.collect.ImmutableList.of;
import static org.assertj.core.api.Assertions.assertThat;

public class FlatteringIteratorTest {

    @Test
    public void correctlyFlattensNestedList() throws Exception {
        Iterator<ImmutableList<String>> iterator = of(
                of("a", "b"),
                of("c", "d", "e"),
                ImmutableList.<String>of(),
                of("f")
        ).iterator();
        CloseableIterator<ImmutableList<String>> inputIterator = CloseableIterators.fromNonCloseableIterator(iterator);
        CrmMappingIteratorFactory.FlatteringIterator<String> flatteringIterator
                = new CrmMappingIteratorFactory.FlatteringIterator<>(inputIterator);
        assertThat(createListFromIterator(flatteringIterator))
                .containsExactly("a", "b", "c", "d", "e", "f");
    }

    private List<String> createListFromIterator(CrmMappingIteratorFactory.FlatteringIterator<String> it) {
        List<String> list = new ArrayList<>();
        it.forEachRemaining(list::add);
        return list;
    }
}
