package ru.yandex.quasar.util;

import androidx.annotation.NonNull;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import com.google.common.base.Optional;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mockito;

import java.util.Collections;
import java.util.List;

import ru.yandex.quasar.core.utils.ChangeObservable;
import ru.yandex.quasar.core.utils.Observable;

@SuppressWarnings({"Guava", "unchecked"})
@RunWith(value = AndroidJUnit4.class)
public class ChangeObservableTest {

    class MyValue {
        private final List<String> items;

        MyValue(List<String> items) {
            this.items = items;
        }
    }

    private class MyObservable extends Observable<MyValue> {
        // nop
    }

    private MyObservable observable;
    private ChangeObservable<MyValue, Boolean> changeObservable;
    private Observable.Observer<Boolean> observer;


    @Before
    public void prepare() {
        observable = new MyObservable();

        changeObservable = new ChangeObservable<MyValue, Boolean>() {
            @NonNull
            @Override
            public Optional deduce(MyValue prev, MyValue next) {
                if (next.items.size() > prev.items.size()) {
                    return Optional.of(Boolean.TRUE);
                } else {
                    return Optional.absent();
                }
            }
        };

        observer = Mockito.mock(Observable.Observer.class);
        changeObservable.addObserver(observer);

        observable.addObserver(changeObservable);

        // put initial value suitable for all tests
        observable.receiveValue(new MyValue(java.util.Arrays.asList("1", "2", "3")));
    }

    @Test
    public void testSubObservableSmoke() {
        observable.receiveValue(new MyValue(java.util.Arrays.asList("1", "2", "3", "4")));

        Mockito.verify(observer).update(Boolean.TRUE);
        Mockito.verifyNoMoreInteractions(observer);
    }

    @Test
    public void testSubObservableTwice() {
        observable.receiveValue(new MyValue(java.util.Arrays.asList("1", "2", "3", "4")));
        observable.receiveValue(new MyValue(java.util.Arrays.asList("1", "2", "3", "4", "5")));

        Mockito.verify(observer, Mockito.times(2)).update(Boolean.TRUE);
        Mockito.verifyNoMoreInteractions(observer);
    }

    @Test
    public void testSubObservableNoChange() {
        observable.receiveValue(new MyValue(java.util.Arrays.asList("1", "2", "3", "4")));
        observable.receiveValue(new MyValue(java.util.Arrays.asList("1", "2", "3", "4")));

        Mockito.verify(observer, Mockito.times(1)).update(Boolean.TRUE);
        Mockito.verifyNoMoreInteractions(observer);
    }

    @Test
    public void testSubObservableUpDown() {
        observable.receiveValue(new MyValue(java.util.Arrays.asList("1", "2")));  // Down
        observable.receiveValue(new MyValue(java.util.Arrays.asList("1", "2", "3")));  // Up

        Mockito.verify(observer, Mockito.times(1)).update(Boolean.TRUE);
        Mockito.verifyNoMoreInteractions(observer);
    }

    @Test
    public void testSubObservableUpDownMuch() {
        observable.receiveValue(new MyValue(Collections.singletonList("1")));  // Down
        observable.receiveValue(new MyValue(java.util.Arrays.asList("1", "2", "3", "4", "5", "6")));  // Up

        Mockito.verify(observer, Mockito.times(1)).update(Boolean.TRUE);
        Mockito.verifyNoMoreInteractions(observer);
    }

}
