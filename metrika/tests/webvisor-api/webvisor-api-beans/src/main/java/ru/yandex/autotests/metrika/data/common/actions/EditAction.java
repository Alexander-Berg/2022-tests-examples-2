package ru.yandex.autotests.metrika.data.common.actions;

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
}
