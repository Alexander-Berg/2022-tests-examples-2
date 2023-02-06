package ru.yandex.quasar.fakes;

import androidx.annotation.NonNull;

import java.io.IOException;

import javax.annotation.Nullable;

import ru.yandex.quasar.data.DataSource;

/**
 * @author Sergey Akimov (akiserg@yandex-team.ru).
 */
public class InMemoryDataSource<T> implements DataSource<T> {
    private volatile T data;

    @Override
    public boolean store(@NonNull T data) throws IOException {
        this.data = data;
        return true;
    }

    @Nullable
    @Override
    public T loadData() throws IOException {
        return data;
    }
}
