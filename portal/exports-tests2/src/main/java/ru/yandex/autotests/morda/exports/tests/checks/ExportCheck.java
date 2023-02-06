package ru.yandex.autotests.morda.exports.tests.checks;

import java.util.function.Consumer;
import java.util.function.Predicate;

/**
 * User: asamar
 * Date: 14.08.2015.
 */
public class ExportCheck<T> implements Consumer<T> {
    private String name;
    private Consumer<T> check;
    private Predicate<T> condition;

    public ExportCheck(String name, Consumer<T> check) {
        this(name, check, (e) -> true);
    }

    public ExportCheck(String name, Consumer<T> check, Predicate<T> condition) {
        this.name = name;
        this.check = check;
        this.condition = condition;
    }

    public String getStory() {
        return name;
    }

    @Override
    public void accept(T t) {
        check.accept(t);
    }

    @Override
    public Consumer<T> andThen(Consumer<? super T> after) {
        return check.andThen(after);
    }

    @Override
    public String toString() {
        return name;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Consumer<T> getCheck() {
        return check;
    }

    public void setCheck(Consumer<T> check) {
        this.check = check;
    }

    public Predicate<T> getCondition() {
        return condition;
    }

    public void setCondition(Predicate<T> condition) {
        this.condition = condition;
    }
}
