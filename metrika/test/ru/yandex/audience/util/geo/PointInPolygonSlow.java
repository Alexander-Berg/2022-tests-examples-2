package ru.yandex.audience.util.geo;

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.GeometryFactory;
import com.vividsolutions.jts.geom.LinearRing;
import com.vividsolutions.jts.geom.MultiPolygon;
import com.vividsolutions.jts.geom.Point;
import com.vividsolutions.jts.geom.Polygon;
import com.vividsolutions.jts.geom.impl.CoordinateArraySequence;

public class PointInPolygonSlow {

    private static final GeometryFactory factory = new GeometryFactory();

    public static final MultiPolygon target = new MultiPolygon(new Polygon[]{
            new Polygon(new LinearRing(new CoordinateArraySequence(new Coordinate[]{
                    new Coordinate(30.871945533265976, 27.707849007413664),
                    new Coordinate(66.55489517945736, 90.33722646721782),
                    new Coordinate(91.93277828687168, 43.64909744232865),
                    new Coordinate(74.99061812554476, 38.65668743593487),
                    new Coordinate(72.75636800328681, 68.32234717598455),
                    new Coordinate(30.871945533265976, 27.707849007413664),
            }), factory), null, factory),
    }, factory);


    public static boolean check(MultiPolygon mp, double x, double y) {
        for (int i = 0; i < mp.getNumGeometries(); i++) {
            if (check((Polygon) mp.getGeometryN(i), x, y)) {
                return true;
            }
        }
        return false;
    }

    public static boolean check(Polygon polygon, double x, double y) {
        int numverts = polygon.getExteriorRing().getNumPoints() - 1;
        double[] xs = new double[numverts];
        double[] ys = new double[numverts];
        for (int i = 0; i < numverts; i++) {
            xs[i] = polygon.getExteriorRing().getCoordinateN(i).x;
            ys[i] = polygon.getExteriorRing().getCoordinateN(i).y;
        }

        return checkSlow(xs, ys, numverts, x, y);
    }

    public static boolean checkSlow(double[] xs, double[] ys, int numverts, double x, double y) {
        double vtx0x = xs[numverts - 1];
        double vtx0y = ys[numverts - 1];
        boolean yflag0 = vtx0y >= y;
        int crossings = 0;
        for (int i = 0, j = numverts + 1; --j > 0; i++) {
            double vtx1x = xs[i];
            double vtx1y = ys[i];
            boolean yflag1 = vtx1y >= y;
            if (yflag0 != yflag1) {
                boolean xflag0 = vtx0x >= x;
                if (xflag0 == (vtx1x >= x)) {
                    if (xflag0) crossings += (yflag0 ? -1 : 1);
                } else {
                    if ((vtx1x - (vtx1y - y) *
                            (vtx0x - vtx1x) / (vtx0y - vtx1y)) >= x) {
                        crossings += (yflag0 ? -1 : 1);
                    }
                }
            }
            yflag0 = yflag1;
            vtx0x = vtx1x;
            vtx0y = vtx1y;
        }
        return crossings != 0;
    }


    public static void main(String[] args) {
        int fail = 0;
        for (int i = 0; i < 1000; i++) {
            for (int j = 0; j < 1000; j++) {
                boolean check = check(target, i / 10.0, j / 10.0);
                boolean check2 = target.intersects(new Point(new CoordinateArraySequence(new Coordinate[]{new Coordinate(i / 10.0, j / 10.0)}), factory));
                if (check != check2) {
                    fail++;
                }
            }
        }
        System.out.println("fail = " + fail);
    }
}
