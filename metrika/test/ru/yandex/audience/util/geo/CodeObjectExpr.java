package ru.yandex.audience.util.geo;

import java.util.HashMap;
import java.util.Map;

public class CodeObjectExpr {
    // геометрия
    // доля обрабатываемой площади в bounding box
    double areaFraction;
    // вероятность точки попасть в эту область.
    // в случае равномерного распределения равна площади выше.
    double probability;

    // логика
    // код
    String text;
    // в случае неточного решения - оценка вероятности ошибки.
    double errorRate;
    // сложность. оценка сложности для исполнения.
    // пока считается среднее количество умножений.
    double complexity;
    // сюда мы положим дополнительные функции, которые нужны чтобы скомпилировать выражение.
    // в случае простого выражения это множество останется пустым.

    Map<String, String> context = new HashMap<>();

    public String getText() {
        return text;
    }

    public void refresh() {
        // do nothing
    }

    public static CodeObjectExpr slow(double areaFraction, double probability, String text, int vert) {
        CodeObjectExpr res = new CodeObjectExpr();
        res.complexity = vert;
        res.errorRate = 0.0;
        res.text = text;
        res.probability = probability;
        res.areaFraction = areaFraction;
        return res;
    }


    public static CodeObjectExpr bilinear(double areaFraction, double probability, String text) {
        CodeObjectExpr res = new CodeObjectExpr();
        res.complexity = 2;
        res.errorRate = 0.0;
        res.text = text;
        res.probability = probability;
        res.areaFraction = areaFraction;
        return res;
    }

    public static CodeObjectExpr linear(double areaFraction, double probability, String text) {
        CodeObjectExpr res = new CodeObjectExpr();
        res.complexity = 1;
        res.errorRate = 0.0;
        res.text = text;
        res.probability = probability;
        res.areaFraction = areaFraction;
        return res;
    }

    public static CodeObjectExpr exactFalse(double areaFraction, double probability) {
        return fixed(areaFraction, probability, "false", 0.0);
    }

    public static CodeObjectExpr exactTrue(double areaFraction, double probability) {
        return fixed(areaFraction, probability, "true", 0.0);
    }

    public static CodeObjectExpr fixed(double areaFraction, double probability, String text, double error) {
        CodeObjectExpr res = new CodeObjectExpr();
        res.complexity = 0;
        res.errorRate = error;
        res.text = text;
        res.probability = probability;
        res.areaFraction = areaFraction;
        return res;
    }
}
