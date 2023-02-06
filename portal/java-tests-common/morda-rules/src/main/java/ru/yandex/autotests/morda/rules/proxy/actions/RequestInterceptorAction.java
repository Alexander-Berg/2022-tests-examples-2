package ru.yandex.autotests.morda.rules.proxy.actions;

/**
 * User: asamar
 * Date: 07.09.2015.
 */
public abstract class RequestInterceptorAction<T, E> extends Action<T> {

    protected E requestInterceptor;
    protected T rule;
    protected boolean isNeed;

    public RequestInterceptorAction(T rule) {
        super(rule);
        this.rule = rule;
        this.isNeed = false;
    }

    public T add(E requestInterceptor){
        this.requestInterceptor = requestInterceptor;
        this.isNeed = true;
        return rule;
    }
}
