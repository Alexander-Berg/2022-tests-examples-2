package ru.yandex.metrika.segments.clickhouse.eval;

import java.util.HashMap;
import java.util.Map;

import javax.annotation.Nonnull;
import javax.annotation.Nullable;

import ru.yandex.metrika.segments.clickhouse.ast.AliasResolver;
import ru.yandex.metrika.segments.clickhouse.ast.Expression;
import ru.yandex.metrika.segments.clickhouse.ast.Name;
import ru.yandex.metrika.segments.clickhouse.types.CHType;

public class MapAliasResolver implements AliasResolver {
    private final Map<Name<?>, Expression<?>> map = new HashMap<>();

    @Nullable
    public <T extends CHType> Expression<T> resolve(Name<T> name) {
        //noinspection unchecked
        return (Expression<T>) map.get(name);
    }

    @Nonnull
    public <T extends CHType> Expression<T> resolveOrThrow(Name<T> name) {
        var resolve = resolve(name);
        if (resolve == null) {
            throw new IllegalArgumentException("Cannot resolve name " + name);
        }
        return resolve;
    }

    public <T extends CHType> void register(Name<T> name, Expression<T> expression) {
        this.map.merge(name, expression, (e1, e2) -> {
            if (e1.equals(e2)) {
                return e1;
            }
            throw new IllegalStateException(
                    "Alias " + name.getName() + " has two different expressions: " +
                            e1 + " and " + e2
            );
        });
    }
}
