package ru.yandex.audience.util.geo;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Random;
import java.util.function.Function;

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.Envelope;
import com.vividsolutions.jts.geom.Geometry;
import com.vividsolutions.jts.geom.GeometryCollection;
import com.vividsolutions.jts.geom.GeometryFactory;
import com.vividsolutions.jts.geom.IntersectionMatrix;
import com.vividsolutions.jts.geom.LineString;
import com.vividsolutions.jts.geom.LinearRing;
import com.vividsolutions.jts.geom.MultiLineString;
import com.vividsolutions.jts.geom.MultiPolygon;
import com.vividsolutions.jts.geom.Point;
import com.vividsolutions.jts.geom.Polygon;
import com.vividsolutions.jts.geom.impl.CoordinateArraySequence;
import org.apache.commons.lang3.ArrayUtils;

import static com.vividsolutions.jts.algorithm.CGAlgorithms3D.distance;

/**
 * http://erich.realtimerendering.com/ptinpoly/
 */
public class PointInPolygon {

    public static final int INIT_DEPTH = 2;
    public static final int DEFAULT_GRID = 16;
    static GeometryFactory factory = new GeometryFactory();

    public static void main(String[] args) {
        checkSpeed();
    }

    private static void checkSpeed() {
        Random r = new Random(42);
        Point[] data = new Point[1000000];
        Arrays.parallelSetAll(data, k-> new Point(new CoordinateArraySequence(new Coordinate[]{
                new Coordinate(100 * r.nextDouble(), 100 * r.nextDouble())
        }), factory));
        for (int j = 0; j < 100; j++) {
            MultiPolygon mp = new MultiPolygon(new Polygon[]{
                    buildRandomPolygon(r, 50)
            }, factory);
            Function<Point, Boolean> pip = buildPointInMultipolygon(mp, DEFAULT_GRID, INIT_DEPTH);
            long start = System.nanoTime();
            for (int i = 0; i < 1000000; i++) {
                pip.apply(data[i]);
            }
            long end = System.nanoTime();
            System.out.println(new Date() + " OK " + mp+"\n"+(end-start)+" nanos");// 1M lookups in 300ms
            System.out.println("cond="+conditioning((Polygon) mp.getGeometryN(0)));
        }
    }

    private static void checkCorrectness() {
        Random r = new Random(42);
        for (int j = 0; j < 100; j++) {
            MultiPolygon mp = new MultiPolygon(new Polygon[]{
                    buildRandomPolygon(r, 50)
            }, factory);
            Function<Point, Boolean> pip = buildPointInMultipolygon(mp, DEFAULT_GRID, INIT_DEPTH);
            for (int i = 0; i < 1000000; i++) {
                Point g = new Point(new CoordinateArraySequence(new Coordinate[]{
                        new Coordinate(100 * r.nextDouble(), 100 * r.nextDouble())
                }), factory);
                if (pip.apply(g) != mp.intersects(g)) {
                    System.out.println("FAIL \nmp " + mp + "\ng = " + g);
                    pip.apply(g);
                    System.exit(1);
                }
            }
            System.out.println(new Date() + " OK " + mp);// 1M lookups in 200ms
        }
    }

    public static double conditioning(Polygon p) {
        Coordinate[] cs = p.getExteriorRing().getCoordinates();
        Envelope env = p.getEnvelopeInternal();
        double diam = Math.max(env.getMaxX() - env.getMinX(), env.getMaxY() - env.getMinY());
        double minD = Double.MAX_VALUE;
        for (int i = 0; i < cs.length - 1; i++) {
            double d = distance(cs[i], cs[i + 1]);
            minD = Math.min(minD, d);
        }
        return diam / minD;
    }

    public static Polygon buildRandomPolygon(Random r, int points) {

        outer:  while (true){
            Coordinate[] cs = new Coordinate[points + 1];
            long start = System.nanoTime();
            for (int i = 0; i < points; i++) {
                LinearRing lr = null;
                do {
                    cs[i] = new Coordinate(100 * r.nextDouble(), 100 * r.nextDouble());
                    cs[i + 1] = cs[0];
                    if (i > 1) {
                        lr = new LinearRing(new CoordinateArraySequence(Arrays.copyOf(cs, i + 2)), factory);
                    }
                    if(System.nanoTime() - start > 10000000000L) {
                        continue outer;
                    }
                } while (i > 1 && !lr.isValid());
            }
            cs[points] = cs[0];
            return new Polygon(new LinearRing(new CoordinateArraySequence(cs), factory), null, factory);
        }
    }

    private static Function<Point, Boolean> buildPointInMultipolygon(MultiPolygon mp, int grid, int depth) {
        Function<Point, Boolean>[] cells = new Function[mp.getNumGeometries()];
        for (int i = 0; i < mp.getNumGeometries(); i++) {
            cells[i] = buildPointInPolygon((Polygon) mp.getGeometryN(i), grid, depth);
        }
        return new Function<Point, Boolean>() {
            @Override
            public Boolean apply(Point g) {
                for (Function<Point, Boolean> cell : cells) {
                    if (cell.apply(g)) return true;
                }
                return false;
            }
        };
    }

    private static Function<Point, Boolean> buildPointInPolygon(Polygon p, int grid, int depth) {
        if(depth != INIT_DEPTH) {
          //  System.out.println("depth = " + depth);
        }
        Envelope env = p.getEnvelopeInternal();

        Function<Point, Boolean>[] cells = new Function[grid * grid];
        for (int i = 0; i < grid; i++) {//x
            for (int j = 0; j < grid; j++) { //y
                double minX = (env.getMaxX() - env.getMinX()) / grid * i;
                double maxX = (env.getMaxX() - env.getMinX()) / grid * (i + 1);
                double minY = (env.getMaxY() - env.getMinY()) / grid * j;
                double maxY = (env.getMaxY() - env.getMinY()) / grid * (j + 1);
                Polygon cell = new Polygon(
                        new LinearRing(new CoordinateArraySequence(new Coordinate[]{
                                new Coordinate(env.getMinX() + minX, env.getMinY() + minY),
                                new Coordinate(env.getMinX() + maxX, env.getMinY() + minY),
                                new Coordinate(env.getMinX() + maxX, env.getMinY() + maxY),
                                new Coordinate(env.getMinX() + minX, env.getMinY() + maxY),
                                new Coordinate(env.getMinX() + minX, env.getMinY() + minY),
                        }), factory),
                        null, factory);
                cells[i + j * grid] = buildCellFunction(cell, p, grid, depth);
            }
        }

        return new Function<Point, Boolean>() {
            @Override
            public Boolean apply(Point g) {
                int gridX = (int) Math.floor((g.getX() - env.getMinX()) / (env.getMaxX() - env.getMinX()) * grid);
                int gridY = (int) Math.floor((g.getY() - env.getMinY()) / (env.getMaxY() - env.getMinY()) * grid);
                if (gridX < 0 || gridX >= grid || gridY < 0 || gridY >= grid) {
                    return false;
                }
                int cell = gridX + gridY * grid;
                return cells[cell].apply(g);
            }
        };
    }

    public static final double EPSILON = 0.000000001;
    public static final double DELTA = 0.00000000001;

    private static Function<Point, Boolean> buildCellFunction(Polygon cell, Polygon p, int grid, int depth) {
        Geometry geomInCell = cell.intersection(p);
        IntersectionMatrix relate = geomInCell.relate(cell);
        if (relate.isCovers() || geomInCell.getArea() / cell.getArea() > 1 - EPSILON) {
            return pp -> true;
        } else if (geomInCell.getArea() / cell.getArea() < EPSILON || geomInCell.getDimension() < 2) {
            // если в клетке пустота, почти пустота или множество меры ноль, то считаем что никого нет.
            return pp -> false;
        } else {
            Geometry bound = cell.intersection(p.getExteriorRing()); // boundary
            if (geomInCell instanceof Polygon) {
                Polygon polyInCell = (Polygon) geomInCell;
                if (bound instanceof MultiLineString) {
                    MultiLineString mls = (MultiLineString) bound;
                    List<LineString> lines = new ArrayList<>();
                    for (int i = 0; i < mls.getNumGeometries(); i++) {
                        if (mls.getGeometryN(i).getLength() > EPSILON && mls.getGeometryN(i).within(cell)) {
                            lines.add((LineString) mls.getGeometryN(i));
                        }
                    }
                    if (lines.size() == 1) { // остался один отрезок
                        return buildLineStringFunction(polyInCell, cell, grid, depth, lines.get(0));
                    }
                    if (lines.size() == 2) { // два разъединенных? отрезка
                        LineString l0 = lines.get(0);
                        LineString l1 = lines.get(1);
                        if (l0.getCoordinateN(0).distance(l1.getCoordinateN(0)) < EPSILON) {
                            LineString l01 = new LineString(new CoordinateArraySequence((Coordinate[]) ArrayUtils.addAll(
                                    l0.reverse().getCoordinates(),
                                    ArrayUtils.remove(l1.getCoordinates(), 0))), factory);
                            return buildLineStringFunction(polyInCell, cell, grid, depth, l01);
                        } else if (l0.getCoordinateN(0).distance(l1.getCoordinateN(l1.getCoordinates().length - 1)) < EPSILON) {
                            LineString l10 = new LineString(new CoordinateArraySequence((Coordinate[]) ArrayUtils.addAll(
                                    l1.getCoordinates(),
                                    ArrayUtils.remove(l0.getCoordinates(), 0))), factory);
                            return buildLineStringFunction(polyInCell, cell, grid, depth, l10);
                        } else if (l0.getCoordinateN(l0.getCoordinates().length - 1).distance(l1.getCoordinateN(0)) < EPSILON) {
                            LineString l01 = new LineString(new CoordinateArraySequence((Coordinate[]) ArrayUtils.addAll(
                                    l0.getCoordinates(),
                                    ArrayUtils.remove(l1.getCoordinates(), 0))), factory);
                            return buildLineStringFunction(polyInCell, cell, grid, depth, l01);
                        } else if (l0.getCoordinateN(l0.getCoordinates().length - 1).distance(l1.getCoordinateN(l1.getCoordinates().length - 1)) < EPSILON) {
                            LineString l10 = new LineString(new CoordinateArraySequence((Coordinate[]) ArrayUtils.addAll(
                                    l1.getCoordinates(),
                                    ArrayUtils.remove(l0.reverse().getCoordinates(), 0))), factory);
                            return buildLineStringFunction(polyInCell, cell, grid, depth, l10);
                        } else {
                            Function<Point, Boolean> f0 = buildLineStringFunction(polyInCell, cell, grid, depth, lines.get(0));
                            Function<Point, Boolean> f1 = buildLineStringFunction(polyInCell, cell, grid, depth, lines.get(1));
                            return pp -> f0.apply(pp) && f1.apply(pp);
                        }
                    }
                    if (depth == 0) {
                        return pp -> false; // в любой непонятной ситуации выливаем точки за борт
                    } else {
                        return buildPointInPolygon(polyInCell, grid, depth - 1);
                    }
                } else if (bound instanceof LineString) {
                    LineString ls = (LineString) bound;
                    return buildLineStringFunction(polyInCell, cell, grid, depth, ls);
                } else if (bound instanceof GeometryCollection) {
                    GeometryCollection gc = (GeometryCollection) bound;
                    List<Geometry> lines = new ArrayList<>();
                    for (int i = 0; i < gc.getNumGeometries(); i++) {
                        if (gc.getGeometryN(i).getLength() > EPSILON) {
                            lines.add(gc.getGeometryN(i));
                        }
                    }
                    if (lines.size() == 1 && lines.get(0) instanceof LineString) {
                        return buildLineStringFunction(polyInCell, cell, grid, depth, (LineString) lines.get(0));
                    } else {
                        if (depth == 0) {
                            System.out.println("max depth reached");
                            return pp -> false; // в любой непонятной ситуации выливаем точки за борт
                        } else {
                            return buildPointInPolygon(polyInCell, grid, depth - 1);
                        }
                    }
                } else {
                    throw new IllegalStateException("unsupported bound " + bound);
                }
            } else if (geomInCell instanceof MultiPolygon) {
                MultiPolygon pmInCell = (MultiPolygon) geomInCell;
                if (depth == 0) {
                    System.out.println("max depth reached");
                    return pp -> false; // в любой непонятной ситуации выливаем точки за борт
                } else {
                    return buildPointInMultipolygon(pmInCell, grid, depth - 1);
                }
            } else {
                throw new IllegalStateException("unsupported geom " + geomInCell);
            }
        }
    }

    // на втором уровне вложенности полигонов некоторые фрагменты линий могут идти вдоль границ клетки, их можно игнорировать
    private static Function<Point, Boolean> buildLineStringFunction(Polygon polyInCell, Polygon cell, int grid, int depth, LineString ls) {
        if (ls.getCoordinates().length == 2) {
            return buildLineFunction(polyInCell.getCentroid(), ls.getCoordinates()[0], ls.getCoordinates()[1]);
        } else {
            boolean isConvex = polyInCell.convexHull().equalsNorm(polyInCell);
            if (isConvex && ls.getCoordinates().length == 3) {
                // если полигон выпуклый, то у нас есть вершина которая углом выпиливает из прямоугольника некий кусок
                // тогда нам надо попасть в те же полуплоскости этих прямых, что и любая другая точка этого полигона
                //
                // также есть вариант что два ребра проходят через cell навылет, без вершины, тогда этот способ тоже норм.
                // еще есть вариант несвязного пересечения, в этом случае код должен упасть в другой ветке.
                Function<Point, Boolean> f0 = buildLineFunction(polyInCell.getCentroid(), ls.getCoordinates()[0], ls.getCoordinates()[1]);
                Function<Point, Boolean> f1 = buildLineFunction(polyInCell.getCentroid(), ls.getCoordinates()[1], ls.getCoordinates()[2]);
                return pp -> f0.apply(pp) && f1.apply(pp);
            } else {
                // если полигон не выпуклый, и он получен из прямоугольника, то у него есть тупой угол и этот угол между ребрами исходного полигона
                // тогда если мы возьмем дополнение, то получим верхний случай, для которого можно посчитать точку и знаки.
                // взять "в лоб" внутреннюю точку невыпуколго p3 нельзя, т.к.
                // во-первых "правильными" комбинациями знаков являются три, ++ +- -+
                // а во-вторых, взятая наугад точка даст нам только один из этих вариантов и мы не сможем выбрать нужные комбинации.
                Geometry g33 = cell.difference(polyInCell);
                if (g33 instanceof Polygon) {
                    Polygon p33 = (Polygon) g33;
                    boolean isConcave = p33.convexHull().equalsNorm(p33);
                    if (isConcave && ls.getCoordinates().length == 3) {
                        Function<Point, Boolean> f0 = buildLineFunction(p33.getCentroid(), ls.getCoordinates()[0], ls.getCoordinates()[1]);
                        Function<Point, Boolean> f1 = buildLineFunction(p33.getCentroid(), ls.getCoordinates()[1], ls.getCoordinates()[2]);
                        return pp -> !f0.apply(pp) || !f1.apply(pp);
                    }
                } else {
                    MultiPolygon mp33 = (MultiPolygon) g33;
                }
            }
        }

        if (depth == 0) {
            return pp -> false; // в любой непонятной ситуации выливаем точки за борт
        } else {
            return buildPointInPolygon(polyInCell, grid, depth - 1);
        }
    }

    /**
     * это неправильно т.к. LineString это связный кусок ломаной произвольной длины, а не отрезок.
     * а MultiLineString - это несколько несвязных ломаных.
     *
     * @param interiorPoint
     * @param p0
     * @param p1
     * @return
     */
    private static Function<Point, Boolean> buildLineFunction(Point interiorPoint, Coordinate p0, Coordinate p1) {
        if (p0.distance(p1) < 0.000001) {
            int z = 42;
        }
        Function<Point, Double> line = pp -> ((pp.getX() - p0.x) * (p1.y - p0.y) - (pp.getY() - p0.y) * (p1.x - p0.x));
        Double apply = line.apply(interiorPoint);
        if (apply > 0) {
            return pp -> line.apply(pp) > 0;
        } else {
            return pp -> line.apply(pp) < 0;
        }
    }

    private static void pInPoly() {
        MultiPolygon mp = new MultiPolygon(new Polygon[]{
                new Polygon(
                        new LinearRing(new CoordinateArraySequence(new Coordinate[]{
                                new Coordinate(42, 42),
                                new Coordinate(43, 42),
                                new Coordinate(42, 43),
                                new Coordinate(42, 42),
                        }), factory),
                        null, factory)
        }, factory);
        Point g = new Point(new CoordinateArraySequence(new Coordinate[]{
                new Coordinate(42.3, 42.3)}), factory);
        for (int i = 0; i < 1000; i++) {
            boolean intersects = mp.intersects(g);
        }
        long l = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            boolean intersects = mp.intersects(g);
        }
        long l2 = System.nanoTime();
        System.out.println("intersects = " + (l2 - l));// 1000 lookups in 63-76 ms
    }


}
