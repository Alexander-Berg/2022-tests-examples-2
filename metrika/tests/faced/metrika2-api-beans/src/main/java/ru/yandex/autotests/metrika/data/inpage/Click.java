package ru.yandex.autotests.metrika.data.inpage;

import java.util.Comparator;
import java.util.Objects;

/**
 * Click object from click map.
 * <p>
 * Click map actually answers with a plain collection of integers
 * that are semantically divided by triples.
 * <p>
 * This class is to split these triples to meaningful objects
 * to support comparisons.
 */
public class Click implements Comparable<Click> {
    private static final Comparator<Click> CLICK_COMPARATOR =
            Comparator.comparingInt(Click::getX).thenComparingInt(Click::getY).thenComparingInt(Click::getT);

    private int x;
    private int y;
    private int t;

    public Click(int x, int y, int t) {
        this.x = x;
        this.y = y;
        this.t = t;
    }

    public int getX() {
        return x;
    }

    public int getY() {
        return y;
    }

    public int getT() {
        return t;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Click click = (Click) o;

        return x == click.x && y == click.y && t == click.t;

    }

    @Override
    public int hashCode() {
        return Objects.hash(x, y, t);
    }

    @Override
    public String toString() {
        return "Click{" +
                "x=" + x +
                ", y=" + y +
                ", t=" + t +
                '}';
    }

    @Override
    public int compareTo(Click o) {
        return CLICK_COMPARATOR.compare(this, o);
    }
}
