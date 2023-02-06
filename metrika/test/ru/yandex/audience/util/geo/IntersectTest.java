package ru.yandex.audience.util.geo;

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.Geometry;
import com.vividsolutions.jts.geom.GeometryFactory;
import com.vividsolutions.jts.geom.LinearRing;
import com.vividsolutions.jts.geom.Polygon;
import com.vividsolutions.jts.geom.impl.CoordinateArraySequence;
import org.junit.Ignore;

@Ignore
public class IntersectTest {
    static GeometryFactory factory = new GeometryFactory();

    public static final Polygon p1 = new Polygon(new LinearRing(new CoordinateArraySequence(new Coordinate[]{
                new Coordinate(3.166572116932842, 48.5390194687463),
                new Coordinate(3.166572116932842, 50.470470727186765),
                new Coordinate(4.180930086918854, 50.470470727186765),
                new Coordinate(4.180930086918854, 48.5390194687463),
                new Coordinate(3.166572116932842, 48.5390194687463),
    }), factory), null, factory);
    public static final Polygon p2 = new Polygon(new LinearRing(new CoordinateArraySequence(new Coordinate[]{
        new Coordinate(2.152214146946829, 50.470470727186765),
                new Coordinate(18.381941666723034, 19.567250592139274),
                new Coordinate(2.390837642830135, 49.228045261718165),
                new Coordinate(2.152214146946829, 50.470470727186765),
    }), factory), null, factory);

    public static void main(String[] args) {
        Geometry intersection = p1.intersection(p2);
        System.out.println("p1 in p2 " + intersection.equalsExact(p1));
        // p1 in p2 true
    }
}
