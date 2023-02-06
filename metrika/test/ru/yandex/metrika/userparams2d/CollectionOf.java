package ru.yandex.metrika.userparams2d;

import java.util.Arrays;
import java.util.Collection;

import org.mockito.ArgumentMatcher;

import ru.yandex.metrika.util.collections.F;

public class CollectionOf<T> implements ArgumentMatcher<Collection<T>> {

    T[] elements;

    @SafeVarargs
    public CollectionOf(T... elements) {
        this.elements = elements;
    }

    @Override
    public boolean matches(Collection<T> object) {
        if (object.size() != elements.length) {
            return false;
        }
        for (T element : elements) {
            if (!object.contains(element)) {
                return false;
            }
        }
        return true;
    }

    public String toString() {
        String elementString = F.join(
                Arrays.asList(elements),
                Object::toString,
                ", ");
        return "[" + elementString + "]";
    }
}
