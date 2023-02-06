package ru.yandex.autotests.metrika.commons.beans;

/**
 * Created by okunev on 06.07.2017.
 */
public class TestObject {

    @Position(1)
    @Column(name = "TestField", type = "Array(Int32)")
    private Integer[] testField;

    public TestObject withTestField(Integer[] testField) {
        this.testField = testField;
        return this;
    }

}
