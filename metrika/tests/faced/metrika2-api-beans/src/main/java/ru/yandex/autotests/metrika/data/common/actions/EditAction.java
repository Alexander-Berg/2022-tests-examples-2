package ru.yandex.autotests.metrika.data.common.actions;

import java.util.function.Function;

/**
 * Created by konkov on 24.04.2015.
 */
public abstract class EditAction<T> {
    private final String title;

    public EditAction(String title) {
        this.title = title;
    }

    public abstract T edit(T source);

    @Override
    public String toString() {
        return title;
    }

    public static <T> EditAction<T> create(String title, Function<T, T> editFunction) {
        return new EditAction<T>(title) {
            @Override
            public T edit(T source) {
                return editFunction.apply(source);
            }
        };
    }

}
