package ru.yandex.autotests.metrika.commons.propertybag;

class User extends PropertyBag<User> {
    public static final PropertyDescriptor<String, User> LOGIN = prop("login", String.class, User.class);
    public static final PropertyDescriptor<String, User> PASSWORD = prop("password", String.class, User.class);
    public static final PropertyDescriptor<String, User> ACCESS_TOKEN = prop("access_token", String.class, User.class);

    @Override
    protected User getThis() {
        return this;
    }
}
