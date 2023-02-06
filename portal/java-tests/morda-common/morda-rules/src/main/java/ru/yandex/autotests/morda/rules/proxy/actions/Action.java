package ru.yandex.autotests.morda.rules.proxy.actions;

/**
 * User: asamar
 * Date: 04.09.2015.
 */
public abstract class Action<T> {
    protected boolean isEnabled = true;
    protected T rule;

    public Action(T rule) {
        this.rule = rule;
    }

    public boolean isEnabled() {
        return isEnabled;
    }

    public T disable() {
        isEnabled = false;
        return rule;
    }

    public T enable() {
        isEnabled = true;
        return rule;
    }

    public T done() {
        return rule;
    }

    public abstract void perform();

    protected void populateFromProperties() {
    }
}
