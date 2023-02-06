package ru.yandex.autotests.metrika.appmetrica.data;

public enum EcomEventType {
    SHOW_SCREEN(1),
    SHOW_PRODUCT_CARD(2),
    SHOW_PRODUCT_DETAILS(3),
    ADD_TO_CART(4),
    REMOVE_FROM_CART(5),
    ORDER(6);

    private int value;

    EcomEventType(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public String getStringValue() {
        return String.valueOf(value);
    }
}
