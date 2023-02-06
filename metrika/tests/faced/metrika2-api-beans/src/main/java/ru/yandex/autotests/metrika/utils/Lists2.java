package ru.yandex.autotests.metrika.utils;

import java.util.ArrayList;
import java.util.List;

public class Lists2 {

    private Lists2() {
    }

    public static <T> List<List<T>> transpose(List<List<T>> arg) {
        List<List<T>> res = new ArrayList<>();
        for (int i = 0; i < arg.size(); i++) {
            List<T> ts = arg.get(i);
            for (int j = 0; j < ts.size(); j++) {
                while(j >= res.size()) {
                    res.add(new ArrayList<>(arg.size()));
                }
                List<T> ts1 = res.get(j);
                ts1.add(ts.get(j));// ts.get(j) =arg[i][j] is now i-th element of ts1, res[j][i]
            }
        }
        return res;
    }

}
