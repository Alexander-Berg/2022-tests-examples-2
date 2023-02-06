package ru.yandex.autotests.metrika.appmetrica.actions;

/**
 * Created by konkov on 15.09.2016.
 */
public abstract class EditAction<TExpected, TUpdate> {
    private final String title;

    public EditAction(String title) {
        this.title = title;
    }

    public abstract TUpdate getUpdate(TExpected source);

    public abstract TExpected edit(TExpected source);

    @Override
    public String toString() {
        return title;
    }
}
