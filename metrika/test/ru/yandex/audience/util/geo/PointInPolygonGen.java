package ru.yandex.audience.util.geo;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import javax.annotation.Nullable;

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.Envelope;
import com.vividsolutions.jts.geom.Geometry;
import com.vividsolutions.jts.geom.GeometryCollection;
import com.vividsolutions.jts.geom.GeometryFactory;
import com.vividsolutions.jts.geom.LineString;
import com.vividsolutions.jts.geom.LinearRing;
import com.vividsolutions.jts.geom.MultiLineString;
import com.vividsolutions.jts.geom.MultiPolygon;
import com.vividsolutions.jts.geom.Point;
import com.vividsolutions.jts.geom.Polygon;
import com.vividsolutions.jts.geom.impl.CoordinateArraySequence;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.tuple.Pair;

import static ru.yandex.audience.util.geo.PointInPolygon.DELTA;
import static ru.yandex.audience.util.geo.PointInPolygon.EPSILON;

public class PointInPolygonGen {
    //разрешение сетки дробления bounding box, используется начиная с конца.
    public static final int[] GRID = new int[] {8,8};
    public static final int INIT_DEPTH = GRID.length - 1;
    static GeometryFactory factory = new GeometryFactory();
    static Random r = new Random(42);

    public static void main(String[] args) {
        for (int j = 0; j < 1000; j++) {
            MultiPolygon mp = new MultiPolygon(new Polygon[]{
                    PointInPolygon.buildRandomPolygon(r, 4)
            }, factory);
            mp.normalize();
            // function name -> function source code.
            Map<String, String> functions = new LinkedHashMap<>();
            // тут мы считаем что в наиболее верхнем случае полигоны могут быть маленькие на большом расстоянии друг от друга,
            // поэтому используем в качестве bounding box ограничения на каждый из них по отдельности
            generatePointInRootMultipolygon(mp, null, INIT_DEPTH, functions, "root_mp", null);
            //if(0 < j && j<500)
            printToClass("Poly" + new DecimalFormat("000").format(j), functions, mp);
            System.out.println(new Date()+" j = " + j);
        }
    }

    private static void generatePointInRootMultipolygon(MultiPolygon mp, @Nullable Envelope env, int depth,
                                                        Map<String, String> functions, String prefix, @Nullable Polygon original) {
        for (int i = 0; i < mp.getNumGeometries(); i++) {
            generatePointInGeometry((Polygon) mp.getGeometryN(i), env, depth, functions, prefix + "_p" + i,
                    original == null ? (Polygon) mp.getGeometryN(i) : original);
        }
        StringBuilder text = new StringBuilder("  public static boolean " + prefix + "(double x, double y) {\n");
        text.append("    return ");
        for (int i = 0; i < mp.getNumGeometries(); i++) {
            if (i > 0) text.append(" || ");
            text.append(prefix).append("_p").append(i).append("(x,y)");
        }
        text.append(";\n");
        text.append("  }\n");
        functions.put(prefix, text.toString());
    }

    private static void generatePointInGeometry(Polygon p, @Nullable Envelope env, int depth,
                                                Map<String, String> functions, String prefix, Polygon original) {
        // если мы еще не знаем ему равен bounding box значит его надо вычислить и его надо проверять.
        // если он уже известен, значит он уже проверен снаружи
        boolean checkBoundingBox = (env == null);
        if (env == null) {
            env = p.getEnvelopeInternal();
            env.expandToInclude(env.getMaxX()+ DELTA, env.getMaxY()+ DELTA);
            env.expandToInclude(env.getMinX()- DELTA, env.getMinY()- DELTA);
        }
        StringBuilder text = new StringBuilder("  // " + p.toString() + "\n" +
                "  public static boolean " + prefix + "(double x, double y) {\n");
        text.append(
                "    double gridX = ((x - " + env.getMinX() + ") * (" + GRID[depth] + " / (" + env.getMaxX() + " - " + env.getMinX() + ") ) );\n" +
                        "    double gridY = ((y - " + env.getMinY() + ") * (" + GRID[depth] + " / (" + env.getMaxY() + " - " + env.getMinY() + ") ) );\n");
        if (checkBoundingBox) {
            text.append(
                    "    if (gridX < 0 || gridX > " + (GRID[depth]+ DELTA) + " || gridY < 0 || gridY > " + (GRID[depth]+ DELTA) + ") {\n" +
                            "      return false;\n" +
                            "    }\n");
        }
        text.append(
                "    int xx = (x==" + env.getMaxX() + ")?" + (GRID[depth] - 1) + ":(int) gridX;\n" +
                        "    int yy = (y==" + env.getMaxY() + ")?" + (GRID[depth] - 1) + ":(int) gridY;\n" +
                        "    int cell = yy + xx * " + GRID[depth] + ";\n");
        text.append("    switch (cell) {\n");

        Map<Integer, String> gridSwitch = new LinkedHashMap<>();
        for (int i = 0; i < GRID[depth]; i++) {//x
            for (int j = 0; j < GRID[depth]; j++) { //y
                double minX = (env.getMaxX() - env.getMinX()) / GRID[depth] * i;
                double maxX = (env.getMaxX() - env.getMinX()) / GRID[depth] * (i + 1);
                double minY = (env.getMaxY() - env.getMinY()) / GRID[depth] * j;
                double maxY = (env.getMaxY() - env.getMinY()) / GRID[depth] * (j + 1);
                Polygon cell = new Polygon(
                        new LinearRing(new CoordinateArraySequence(new Coordinate[]{
                                new Coordinate(env.getMinX() + minX, env.getMinY() + minY),
                                new Coordinate(env.getMinX() + maxX, env.getMinY() + minY),
                                new Coordinate(env.getMinX() + maxX, env.getMinY() + maxY),
                                new Coordinate(env.getMinX() + minX, env.getMinY() + maxY),
                                new Coordinate(env.getMinX() + minX, env.getMinY() + minY),
                        }), factory),
                        null, factory);
                cell.normalize();
                gridSwitch.put(i * GRID[depth] + j, generateCellFunction(cell, p, depth, functions, prefix + "_c" + (i * GRID[depth] + j), original) + "\n");
            }
        }
        for (Map.Entry<Integer, String> ee : gridSwitch.entrySet()) {
            text.append("      case " + ee.getKey() + ": " + ee.getValue());
        }
       /* Map<String, List<Integer>> cellsByFunction = gridSwitch.entrySet().stream().collect(Collectors.groupingBy(e -> e.getValue(),
                Collectors.mapping(e -> e.getKey(), Collectors.toList())));
        for (Map.Entry<String, List<Integer>> ee : cellsByFunction.entrySet()) {
            for (Integer val : ee.getValue()) {
                text.append("      case "+val+": \n");
            }
            text.append("          "+ee.getKey());
        }*/
        text.append("    }\n" +
                "    // unreachable\n" +
                "    return false;\n" +
                "  }\n");
        functions.put(prefix, text.toString());
    }

    private static String generateCellFunction(Polygon cell, Polygon p, int depth,
                                               Map<String, String> functions, String prefix, Polygon original) {
        Geometry geomInCell = null;
        try {
            geomInCell = cell.intersection(p); // эта штука может глючить. и может падать.
        } catch (Exception e) {
            return generateCellFunction(move(cell), p, depth, functions, prefix, original);
        }
        if (geomInCell.getArea() / cell.getArea() > 1 - EPSILON) {
            // если мы видим что клетка почти полностью лежит в полигоне, то на всякий случай проверяем что там же лежат ее вершины
            // достаточно маловероятный кейс, что они не будут внутри, если только это не баг, и если это баг то мы считаем что клетка лежит снаружи полигона.
            int points = 0;
            if(p.covers(new Point(new CoordinateArraySequence(new Coordinate[]{cell.getExteriorRing().getCoordinateN(0)}), factory))) points++;
            if(p.covers(new Point(new CoordinateArraySequence(new Coordinate[]{cell.getExteriorRing().getCoordinateN(1)}), factory))) points++;
            if(p.covers(new Point(new CoordinateArraySequence(new Coordinate[]{cell.getExteriorRing().getCoordinateN(2)}), factory))) points++;
            if(p.covers(new Point(new CoordinateArraySequence(new Coordinate[]{cell.getExteriorRing().getCoordinateN(3)}), factory))) points++;
            if(points >= 2) {
                return "return true;";
            } else {
                return "return false;"; // bug is here, fix it
            }
        } else if (geomInCell.getArea() / cell.getArea() < EPSILON || geomInCell.getDimension() < 2) {
            //см предыдущий комментарий.
            int points = 0;
            if(p.covers(new Point(new CoordinateArraySequence(new Coordinate[]{cell.getExteriorRing().getCoordinateN(0)}), factory))) points++;
            if(p.covers(new Point(new CoordinateArraySequence(new Coordinate[]{cell.getExteriorRing().getCoordinateN(1)}), factory))) points++;
            if(p.covers(new Point(new CoordinateArraySequence(new Coordinate[]{cell.getExteriorRing().getCoordinateN(2)}), factory))) points++;
            if(p.covers(new Point(new CoordinateArraySequence(new Coordinate[]{cell.getExteriorRing().getCoordinateN(3)}), factory))) points++;
            if(points <= 2) {
                return "return false;";
            } else {
                return "return true;";
            }
        } else {
            Geometry bound = cell.intersection(p.getBoundary());
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
                        return "return " + generateLineStringFunction(polyInCell, cell, depth, lines.get(0), functions, prefix, original) + ";";
                    }
                    if (lines.size() == 2) { // два разъединенных? отрезка
                        LineString l0 = lines.get(0);
                        LineString l1 = lines.get(1);
                        if (l0.getCoordinateN(0).distance(l1.getCoordinateN(0)) < EPSILON) {
                            LineString l01 = new LineString(new CoordinateArraySequence(ArrayUtils.addAll(
                                    l0.reverse().getCoordinates(),
                                    ArrayUtils.remove(l1.getCoordinates(), 0))), factory);
                            return "return " + generateLineStringFunction(polyInCell, cell, depth, l01, functions, prefix, original) + ";";
                        } else if (l0.getCoordinateN(0).distance(l1.getCoordinateN(l1.getCoordinates().length - 1)) < EPSILON) {
                            LineString l10 = new LineString(new CoordinateArraySequence(ArrayUtils.addAll(
                                    l1.getCoordinates(),
                                    ArrayUtils.remove(l0.getCoordinates(), 0))), factory);
                            return "return " + generateLineStringFunction(polyInCell, cell, depth, l10, functions, prefix, original) + ";";
                        } else if (l0.getCoordinateN(l0.getCoordinates().length - 1).distance(l1.getCoordinateN(0)) < EPSILON) {
                            LineString l01 = new LineString(new CoordinateArraySequence(ArrayUtils.addAll(
                                    l0.getCoordinates(),
                                    ArrayUtils.remove(l1.getCoordinates(), 0))), factory);
                            return "return " + generateLineStringFunction(polyInCell, cell, depth, l01, functions, prefix, original) + ";";
                        } else if (l0.getCoordinateN(l0.getCoordinates().length - 1).distance(l1.getCoordinateN(l1.getCoordinates().length - 1)) < EPSILON) {
                            LineString l10 = new LineString(new CoordinateArraySequence(ArrayUtils.addAll(
                                    l1.getCoordinates(),
                                    ArrayUtils.remove(l0.reverse().getCoordinates(), 0))), factory);
                            return "return " + generateLineStringFunction(polyInCell, cell, depth, l10, functions, prefix, original) + ";";
                        } else {
                            String f0 = generateLineStringFunction(polyInCell, cell, depth, lines.get(0), functions, prefix, original);
                            String f1 = generateLineStringFunction(polyInCell, cell, depth, lines.get(1), functions, prefix, original);
                            if (f0.contains(prefix)) {
                                return "return " + f0 + ";";
                            } else if (f1.contains(prefix)) {
                                return "return " + f1 + ";";
                            } else {
                                // если условия "простые" то они нужны оба. если условие превратилось во вложенный вызов - то можно оставить одно из них.
                                return "return " + f0 + " && " + f1 + ";";
                            }
                        }
                    }
                    if (depth == 0) {
                        generateExactCheck(polyInCell, functions, prefix+"_p", original);
                        return "return " + prefix + "_p(x,y);";
                        //return "//max depth reached\n" +
                        //        " return " + (geomInCell.getArea() / cell.getArea() < 0.5 ? "false;\n" : "true;\n"); // в любой непонятной ситуации выливаем точки за борт
                    } else {
                        generatePointInGeometry(polyInCell, cell.getEnvelopeInternal(), depth - 1, functions, prefix + "_p", original);
                        return "return " + prefix + "_p(x,y);";
                    }
                } else if (bound instanceof LineString) {
                    LineString ls = (LineString) bound;
                    return "return " + generateLineStringFunction(polyInCell, cell, depth, ls, functions, prefix, original) + ";";
                } else if (bound instanceof GeometryCollection) {
                    GeometryCollection gc = (GeometryCollection) bound;
                    List<Geometry> lines = new ArrayList<>();
                    for (int i = 0; i < gc.getNumGeometries(); i++) {
                        if (gc.getGeometryN(i).getLength() > EPSILON) {
                            lines.add(gc.getGeometryN(i));
                        }
                    }
                    if (lines.size() == 1 && lines.get(0) instanceof LineString) {
                        return "return " + generateLineStringFunction(polyInCell, cell, depth, (LineString) lines.get(0), functions, prefix, original) + ";";
                    } else {
                        if (depth == 0) {
                            generateExactCheck(polyInCell, functions, prefix+"_p", original);
                            return "return " + prefix + "_p(x,y);";
                            //System.out.println("max depth reached");
                            //return "//max depth reached\n" +
                            //        " return " + (geomInCell.getArea() / cell.getArea() < 0.5 ? "false;\n" : "true;\n"); // в любой непонятной ситуации выливаем точки за борт
                        } else {
                            generatePointInGeometry(polyInCell, cell.getEnvelopeInternal(), depth - 1, functions, prefix + "_p", original);
                            return "return " + prefix + "_p(x,y);";
                        }
                    }
                } else {
                    throw new IllegalStateException("unsupported bound " + bound);
                }
            } else if (geomInCell instanceof MultiPolygon) {
                MultiPolygon pmInCell = (MultiPolygon) geomInCell;
                if (depth == 0) {
                    generateExactCheck(pmInCell, functions, prefix+"_mp", original);
                    return "return " + prefix + "_mp(x,y);";
                    //System.out.println("max depth reached");
                    //return "//max depth reached\n" +
                    //        " return " + (geomInCell.getArea() / cell.getArea() < 0.5 ? "false;\n" : "true;\n"); // в любой непонятной ситуации выливаем точки за борт
                } else {
                    generatePointInRootMultipolygon(pmInCell, cell.getEnvelopeInternal(), depth - 1, functions, prefix + "_mp", original);
                    // в некоторых случаях это дает более простой код, а иногда - более сложный.
                    //generatePointInGeometry(pmInCell, cell.getEnvelopeInternal(), grid, depth - 1, functions, prefix + "_mp");
                    return "return " + prefix + "_mp(x,y);";
                }
            } else {
                throw new IllegalStateException("unsupported geom " + geomInCell);
            }
        }
    }

    private static void generateExactCheck(MultiPolygon polyInCell, Map<String, String> functions, String prefix, Polygon original) {
        for (int i = 0; i < polyInCell.getNumGeometries(); i++) {
            Polygon poly = (Polygon) polyInCell.getGeometryN(i);
            generateExactCheck(poly, functions, prefix+"p"+i, original);
        }
        String text = "  public static boolean "+prefix+"(double x, double y) {\n" +
                "    return "+(IntStream.range(0, polyInCell.getNumGeometries()).mapToObj(i-> prefix+"p"+i+"(x,y)")).collect(Collectors.joining(" || "))+";\n"+
                "  }\n";
        functions.put(prefix, text);
    }

    private static void generateExactCheck(Polygon polyInCell, Map<String, String> functions, String prefix, Polygon original) {
        StringBuilder text = new StringBuilder();
        Coordinate[] cs = polyInCell.getExteriorRing().getCoordinates();
        String px = prefix+"_x";
        String py = prefix+"_y";
        int numver = polyInCell.getExteriorRing().getNumPoints() - 1;
        text.append("  public static final double[] "+px+" = new double[] {"+Arrays.stream(cs,0,numver).map(c->""+c.x).collect(Collectors.joining(","))+"};\n");
        text.append("  public static final double[] "+py+" = new double[] {"+Arrays.stream(cs,0,numver).map(c->""+c.y).collect(Collectors.joining(","))+"};\n");
        text.append("  public static boolean "+prefix+"(double x, double y) {\n" +
                "    return checkSlow("+px+", "+py+", "+numver+", x, y);\n" +
                "  }\n");

        functions.put(prefix, text.toString());
    }

    // сдвигает прямоугольник в случайном направлении на небольшое расстояние.
    private static Polygon move(Polygon cell) {
        double phi = r.nextDouble() * Math.PI * 2;
        double deltaX = Math.cos(phi) * EPSILON / 100;
        double deltaY = Math.sin(phi) * EPSILON / 100;

        LineString ls = cell.getExteriorRing();
        Polygon moved = new Polygon(
                new LinearRing(new CoordinateArraySequence(new Coordinate[]{
                        new Coordinate(ls.getCoordinateN(0).x + deltaX, ls.getCoordinateN(0).y + deltaY),
                        new Coordinate(ls.getCoordinateN(1).x + deltaX, ls.getCoordinateN(1).y + deltaY),
                        new Coordinate(ls.getCoordinateN(2).x + deltaX, ls.getCoordinateN(2).y + deltaY),
                        new Coordinate(ls.getCoordinateN(3).x + deltaX, ls.getCoordinateN(3).y + deltaY),
                        new Coordinate(ls.getCoordinateN(4).x + deltaX, ls.getCoordinateN(4).y + deltaY),
                }), factory),
                null, factory);

        return moved;
    }

    private static String generateLineStringFunction(Polygon polyInCell, Polygon cell, int depth, LineString ls, Map<String, String> functions, String prefix, Polygon original) {
        if (ls.getCoordinates().length == 2) {
            return generateLineFunction(polyInCell.getCentroid(), ls.getCoordinates()[0], ls.getCoordinates()[1], true, original);
        } else {
            boolean isConvex = polyInCell.convexHull().equalsNorm(polyInCell);
            if (isConvex && ls.getCoordinates().length == 3) {
                // если полигон выпуклый, то у нас есть вершина которая углом выпиливает из прямоугольника некий кусок
                // тогда нам надо попасть в те же полуплоскости этих прямых, что и любая другая точка этого полигона
                //
                // также есть вариант что два ребра проходят через cell навылет, без вершины, тогда этот способ тоже норм.
                // еще есть вариант несвязного пересечения, в этом случае код должен упасть в другой ветке.
                String f0 = generateLineFunction(polyInCell.getCentroid(), ls.getCoordinates()[0], ls.getCoordinates()[1], true, original);
                String f1 = generateLineFunction(polyInCell.getCentroid(), ls.getCoordinates()[1], ls.getCoordinates()[2], true, original);
                return "(" + f0 + " && " + f1 + ")";//pp -> f0.apply(pp) && f1.apply(pp);
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
                        String f0 = generateLineFunction(p33.getCentroid(), ls.getCoordinates()[0], ls.getCoordinates()[1], false, original);
                        String f1 = generateLineFunction(p33.getCentroid(), ls.getCoordinates()[1], ls.getCoordinates()[2], false, original);
                        return "!(" + f0 + " && " + f1 + ")";//pp -> !f0.apply(pp) || !f1.apply(pp);
                    }
                } else {
                    MultiPolygon mp33 = (MultiPolygon) g33;
                }
            }
        }

        if (depth == 0) {
            generateExactCheck(polyInCell, functions, prefix+"_p", original);
            return prefix + "_p(x,y)";
            //return (polyInCell.getArea() / cell.getArea() < 0.5 ? "false" : "true"); // в любой непонятной ситуации выливаем точки за борт
        } else {
            // is this name unique?
            generatePointInGeometry(polyInCell, cell.getEnvelopeInternal(), depth - 1, functions, prefix + "_lp", original);
            return prefix + "_lp(x,y)";
        }
    }

    private static String generateLineFunction(Point interiorPoint, Coordinate p0, Coordinate p1, boolean closed, Polygon original) {
        Pair<Coordinate, Coordinate> pps = findOriginalPoints(p0, p1, original);
        Coordinate pp0 = pps.getLeft();
        Coordinate pp1 = pps.getRight();
        Function<Point, Double> line = pp -> ((pp.getX() - pp0.x) * (pp1.y - pp0.y) - (pp.getY() - pp0.y) * (pp1.x - pp0.x));
        Double apply = line.apply(interiorPoint);
        return "((x - " + pp0.x + ") * (" + pp1.y + " - " + pp0.y + ") - (y - " + pp0.y + ") * (" + pp1.x + " - " + pp0.x + ")) " +
                (closed ? (apply > 0 ? ">= " + (-DELTA) : "<= " + DELTA) : (apply > 0 ? "> 0" : "< 0"));
    }

    private static Pair<Coordinate, Coordinate> findOriginalPoints(Coordinate p0, Coordinate p1, Polygon original) {
        for (int i = 0; i < original.getExteriorRing().getCoordinates().length; i++) {
            Coordinate pp0 = original.getExteriorRing().getCoordinates()[i];
            Coordinate pp1 = original.getExteriorRing().getCoordinates()[i + 1];
            if (Math.abs((pp0.x - pp1.x) * (p0.y - p1.y) - (p0.x - p1.x) * (pp0.y - pp1.y)) < EPSILON) {
                return Pair.of(pp0, pp1);
            }
        }
        return Pair.of(p0, p1);
    }

    private static void printToClass(String className, Map<String, String> functions, MultiPolygon mp) {
        try (BufferedWriter fr = new BufferedWriter(new FileWriter(new File("/home/orantius/dev/projects/metrika/api/metrika-api/audience-common/src/test/ru/yandex/audience/util/geo/" + className + ".java")))) {
            fr.write(
                    "package ru.yandex.audience.util.geo;\n\n" +
                            "import com.vividsolutions.jts.geom.*;\n" +
                            "import com.vividsolutions.jts.geom.impl.CoordinateArraySequence;\n" +
                            "import org.apache.commons.lang3.tuple.Pair;\n" +
                            "import java.util.Date;\n" +
                            "\n" +
                            "//" + mp.toText() + "\n\n" +
                            "public class " + className + " {\n\n" +
                            "  private static final GeometryFactory factory = new GeometryFactory();\n\n" +
                            "  public static final MultiPolygon target = new MultiPolygon(new Polygon[]{\n");
            for (int i = 0; i < mp.getNumGeometries(); i++) {
                Polygon p = (Polygon) mp.getGeometryN(i);
                // new Polygon(new LinearRing(new CoordinateArraySequence(cs), factory), null, factory);
                fr.write("    new Polygon(new LinearRing(new CoordinateArraySequence(new Coordinate[]{\n");
                for (Coordinate cd : p.getExteriorRing().getCoordinates()) {
                    fr.write("      new Coordinate(" + cd.x + "," + cd.y + "),\n");
                }
                fr.write("    }), factory), null, factory),\n");
            }
            fr.write("  }, factory);\n\n");
            for (Map.Entry<String, String> ee : functions.entrySet()) {
                fr.write(ee.getValue());
                fr.newLine();
            }
            fr.write("  private static boolean checkSlow(double[] xs, double[] ys, int numverts, double x, double y) {\n" +
                    "      double vtx0x = xs[numverts - 1];\n" +
                    "      double vtx0y = ys[numverts - 1];\n" +
                    "      boolean yflag0 = vtx0y >= y;\n" +
                    "      int crossings = 0;\n" +
                    "      for (int i = 0, j = numverts + 1; --j > 0; i++) {\n" +
                    "        double vtx1x = xs[i];\n" +
                    "        double vtx1y = ys[i];\n" +
                    "        boolean yflag1 = vtx1y >= y;\n" +
                    "        if (yflag0 != yflag1) {\n" +
                    "          boolean xflag0 = vtx0x >= x;\n" +
                    "          if (xflag0 == (vtx1x >= x)) {\n" +
                    "            if (xflag0) crossings += (yflag0 ? -1 : 1);\n" +
                    "          } else {\n" +
                    "            if ((vtx1x - (vtx1y - y) *\n" +
                    "                    (vtx0x - vtx1x) / (vtx0y - vtx1y)) >= x) {\n" +
                    "                crossings += (yflag0 ? -1 : 1);\n" +
                    "            }\n" +
                    "          }\n" +
                    "        }\n" +
                    "        yflag0 = yflag1;\n" +
                    "        vtx0x = vtx1x;\n" +
                    "        vtx0y = vtx1y;\n" +
                    "      }\n" +
                    "      return crossings != 0;\n" +
                    "    }\n\n");
            fr.write("  public static Pair<Long,Integer> test(double[] xs, double[] ys) {\n" +
                    "    int failCount = 0;\n" +
                    "    for (int j = 0; j < 10; j++) {\n" +
                    "      for (int i = 0; i < 1000000; i++) {\n" +
                    "        boolean b = root_mp(xs[i], ys[i]);\n" +
                    "        if (!b) {\n" +
                    "          failCount++;\n" +
                    "        }\n" +
                    "      }\n" +
                    "    }\n" +
                    "    int okCount = 0;\n" +
                    "    long start = System.currentTimeMillis();\n" +
                    "    for (int i = 0; i < 1000000; i++) {\n" +
                    "      boolean b = root_mp(xs[i], ys[i]);\n" +
                    "      if(b){\n" +
                    "        okCount++;\n" +
                    "      }\n" +
                    "    }\n" +
                    "    long end = System.currentTimeMillis();\n" +
                    "    if(failCount < 0) \n" +
                    "      System.out.println(new Date() + \" "+ className +" OK \"+ target +\"\\n\" + (end - start) + \" ms, fail count=\"+failCount+\" ok \"+okCount);\n" +
                    "    return Pair.of((end - start), failCount);\n" +
                    "  }\n\n");
            fr.write("  public static Pair<Long,Integer> testSlow(double[] xs, double[] ys) {\n" +
                    "    int failCount = 0;\n" +
                    "    for (int i = 0; i < 1000000; i++) {\n" +
                    "      boolean intersects = target.intersects(new Point(new CoordinateArraySequence(new Coordinate[]{\n" +
                    "              new Coordinate(xs[i], ys[i])\n" +
                    "      }), factory));\n" +
                    "      boolean b = root_mp(xs[i], ys[i]);\n" +
                    "      if(b != intersects) {\n" +
                    "        failCount++;\n" +
                    "      }\n" +
                    "    }\n" +
                    "    int okCount = 0;\n" +
                    "    long start = System.currentTimeMillis();\n" +
                    "    for (int i = 0; i < 1000000; i++) {\n" +
                    "      boolean b = root_mp(xs[i], ys[i]);\n" +
                    "      if(b){\n" +
                    "        okCount++;\n" +
                    "      }\n" +
                    "    }\n" +
                    "    long end = System.currentTimeMillis();\n" +
                    "    if(failCount > 0) System.out.println(new Date() + \" " + className + " OK \" + target +\"\\n\" + (end - start) + \" ms, fail count=\"+failCount+\" ok \"+okCount);\n" +
                    "    return Pair.of((end - start), failCount);\n" +
                    "  }\n");
            fr.write("}\n");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
