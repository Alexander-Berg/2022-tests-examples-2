package ru.yandex.autotests.metrika.utils;

import org.junit.Test;

import static org.junit.Assert.*;
import static java.util.Arrays.asList;

public class Lists2Test {

    @Test
    public void simple() throws Exception {
        assertEquals(asList(asList(1,3,5), asList(2,4,6)), Lists2.transpose(asList(asList(1,2),asList(3,4), asList(5,6))));
    }

    @Test
    public void empty() throws Exception {
        assertEquals(asList(), Lists2.transpose(asList(asList(),asList(), asList())));
    }

    @Test
    public void triangle() throws Exception {
        assertEquals(asList(asList(1,2,4), asList(3,5), asList(6)), Lists2.transpose(asList(asList(1),asList(2,3), asList(4,5,6))));
    }

    @Test
    public void triangle2() throws Exception {
        assertEquals(asList(asList(1,4,6), asList(2,5), asList(3)), Lists2.transpose(asList(asList(1,2,3),asList(4,5), asList(6))));
    }

    /**
     * тут мы видим как transpose ведет себя на совсем не прямоугольном аргументе, а именно
     * по второму индексу у нас оказывается список вторых элементов исходных списков, что строго говоря приводит к потере "формы"
     * аргументом, что в нашем случае не важно. если забивать пропущенные индексы null-ами, то например форма изменится при обратном преобразовании -
     * некоторые списки начнут заканчиваться на null, в тех местах где раньше вообще не было элементов.
     */
    @Test
    public void triangle3() throws Exception {
        assertEquals(asList(asList(1,2,4), asList(3)), Lists2.transpose(asList(asList(1),asList(2,3), asList(4))));
    }

    @Test
    public void column() throws Exception {
        assertEquals(asList(asList(1), asList(2), asList(3), asList(4)), Lists2.transpose(asList(asList(1,2,3,4))));
    }

    @Test
    public void involution() throws Exception {
        assertEquals(asList(asList(1,2),asList(3,4), asList(5,6)), Lists2.transpose(Lists2.transpose(asList(asList(1,2),asList(3,4), asList(5,6)))));
    }

    @Test
    public void testNull() throws Exception {
        assertEquals(asList(asList(1,null,5), asList(null,4,null)), Lists2.transpose(asList(asList(1,null),asList(null,4), asList(5,null))));
    }

}