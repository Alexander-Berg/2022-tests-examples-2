package ru.yandex.audience.util.geo;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.text.DecimalFormat;
import java.util.Random;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.vividsolutions.jts.geom.Coordinate;
import com.vividsolutions.jts.geom.GeometryFactory;
import com.vividsolutions.jts.geom.MultiPolygon;
import com.vividsolutions.jts.geom.Polygon;
import org.junit.Ignore;

import static ru.yandex.audience.util.geo.PointInPolygon.buildRandomPolygon;

// генерит классы такого размера, что javac отказывается их компилить.
@Ignore("Force ant not to pick this class as JUnit test")
public class GenTestData {
    // сколько полигонов
    public static final int ARGS = 1000;
    // сколько точек в полигоне
    public static final int POINTS = 10;

    static final GeometryFactory factory = new GeometryFactory();
    static final Random r = new Random(42);
    private static final DecimalFormat decimalFormat= new DecimalFormat("000");

    public static void main(String[] args) throws Exception {

        String className = "Data"+ POINTS;
        try (BufferedWriter fr = new BufferedWriter(new FileWriter(new File(
                "/home/orantius/dev/projects/metrika/api/metrika-api/audience-common/src/test/ru/yandex/audience/util/geo/" + className + ".java")))) {
            fr.write(
                    "package ru.yandex.audience.util.geo;\n\n" +
                        "import com.vividsolutions.jts.geom.*;\n" +
                        "import com.vividsolutions.jts.geom.impl.CoordinateArraySequence;\n" +
                        "import org.apache.commons.lang3.tuple.Pair;\n" +
                        "import java.util.Date;\n" +
                        "\n" +
                        "public class " + className + " {\n\n" +
                        "  private static final GeometryFactory factory = new GeometryFactory();\n\n");
            for (int j = 0; j < ARGS; j++) {
                MultiPolygon mp = new MultiPolygon(new Polygon[]{
                        buildRandomPolygon(r, POINTS)
                }, factory);
                fr.write("  public static final MultiPolygon target"+ decimalFormat.format(j)+" = new MultiPolygon(new Polygon[]{\n");
                for (int i = 0; i < mp.getNumGeometries(); i++) {
                    Polygon p = (Polygon) mp.getGeometryN(i);
                    fr.write("    new Polygon(new LinearRing(new CoordinateArraySequence(new Coordinate[]{\n");
                    for (Coordinate cd : p.getExteriorRing().getCoordinates()) {
                        fr.write("      new Coordinate(" + cd.x + "," + cd.y + "),\n");
                    }
                    fr.write("    }), factory), null, factory),\n");
                }
                fr.write("  }, factory);\n\n");
            }

            fr.write("  public static final MultiPolygon[] target = {" +
                            IntStream.range(0, ARGS/10).mapToObj(i->
                                    IntStream.range(0,10).mapToObj(j->"target"+ decimalFormat.format(i*10+j))
                                            .collect(Collectors.joining(", ")))
                            .collect(Collectors.joining(",\n"))
                                            +"};\n");
            fr.write("}\n");
        }
    }
}
