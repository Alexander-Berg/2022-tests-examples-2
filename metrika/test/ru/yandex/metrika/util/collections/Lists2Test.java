package ru.yandex.metrika.util.collections;

import java.util.ArrayList;
import java.util.List;

import org.junit.Test;

import static org.assertj.core.api.Assertions.assertThat;


public class Lists2Test {

    @Test
    public void byteArrayJoin() {
        byte[] arr1 = new byte[]{1, 2, 3};
        byte[] arr2 = new byte[]{4, 5};
        byte[] arr3 = new byte[]{6};

        List<byte[]> list = new ArrayList<>();
        list.add(arr1);
        list.add(arr2);
        list.add(arr3);

        byte[] joined = Lists2.join(list, (byte) 10);
        assertThat(joined).hasSize(8);
        assertThat(joined).containsExactly(1, 2, 3, 10, 4, 5, 10, 6);
    }
}
