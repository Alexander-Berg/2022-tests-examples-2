package ru.yandex.audience.util.geo;

import java.util.Collection;

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.GeometryFactory;
import com.vividsolutions.jts.geom.LinearRing;
import com.vividsolutions.jts.geom.MultiPolygon;
import com.vividsolutions.jts.geom.Polygon;
import com.vividsolutions.jts.geom.impl.CoordinateArraySequence;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.util.GeoHashUtilsRedis;

import static org.junit.Assert.assertEquals;

public class GeoHashUtilsRedisTest {

    private GeoHashUtilsRedis target;
    private GeometryFactory factory;

    @Before
    public void setUp() throws Exception {
        target = new GeoHashUtilsRedis();
        factory = new GeometryFactory();
    }

    @Test
    public void polygonHashes() throws Exception {
        Collection<Long> longs = target.polygonHashes(new MultiPolygon(new Polygon[]{
                new Polygon(
                        new LinearRing(new CoordinateArraySequence(new Coordinate[]{
                                new Coordinate(42, 42),
                                new Coordinate(43, 42),
                                new Coordinate(42, 43),
                                new Coordinate(42, 42),
                        }), factory),
                        null, factory)
        }, factory));
        assertEquals(longs.size(), 2325);
    }

}
