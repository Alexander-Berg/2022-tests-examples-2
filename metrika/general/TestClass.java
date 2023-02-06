package ru.yandex.metrika.util.tanker;

import ru.yandex.metrika.util.locale.TankerIgnore;

/**
 * @author orantius
 * @version $Id$
 * @since 12/23/13
 */
@TestAnnotation("абв type")
@TankerIgnore
public class TestClass {

    private static final String staticField ="ыы static field";
    private static final String staticField2;
    static {staticField2 = "абв static ";}

    @TestAnnotation("абв field")
    private String instanceField ="ыы instance field";
    private String instanceField2 ="ыы instance field";
    {instanceField2 = "абв instance";}

    @TestAnnotation("абв constructor")
    public TestClass(@TestAnnotation("абв param") String str) {
        instanceField  =str;
    }

    @TestAnnotation("абв method")
    public static void main(String[] args) {
        TestClass tcx = new TestClass("вв");
        @TestAnnotation("абв local")  // doesn't work
        String local = "local строка";
    }
}
