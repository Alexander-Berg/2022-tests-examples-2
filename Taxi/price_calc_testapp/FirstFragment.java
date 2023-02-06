package ru.yandex.price_calc_testapp;

import android.os.Bundle;
import android.os.SystemClock;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.navigation.fragment.NavHostFragment;

import java.util.ArrayList;
import java.util.Random;
import java.util.concurrent.TimeUnit;

import io.reactivex.rxjava3.android.schedulers.AndroidSchedulers;
import io.reactivex.rxjava3.core.Observable;
import io.reactivex.rxjava3.disposables.Disposable;
import io.reactivex.rxjava3.schedulers.Schedulers;
import ru.yandex.pricecalc.CompositePrice;
import ru.yandex.pricecalc.InterpreterResult;
import ru.yandex.pricecalc.MovementPoint;
import ru.yandex.pricecalc.PriceCalc;

import static ru.yandex.price_calc_testapp.TestData.BYTECODE_return_price_x_0_9;
import static ru.yandex.price_calc_testapp.TestData.POLYGONS;
import static ru.yandex.price_calc_testapp.TestData.POLYGONS_HELSINKI;
import static ru.yandex.price_calc_testapp.TestData.PRICES_1;
import static ru.yandex.price_calc_testapp.TestData.PRICES_2;
import static ru.yandex.price_calc_testapp.TestData.PRICES_HELSINKI;
import static ru.yandex.price_calc_testapp.TestData.TRIP_DETAILS;

public class FirstFragment extends Fragment {

    Disposable disposable = Disposable.disposed();
    TextView textView;

    @Override
    public View onCreateView(
            LayoutInflater inflater, ViewGroup container,
            Bundle savedInstanceState
    ) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_first, container, false);
    }

    public void onViewCreated(@NonNull View view, Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        textView = view.findViewById(R.id.textview_first);

        view.findViewById(R.id.button_first).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                NavHostFragment.findNavController(FirstFragment.this)
                        .navigate(R.id.action_FirstFragment_to_SecondFragment);
            }
        });

        ArrayList<MovementPoint> points = buildRandomTrack(10000);

        disposable = Observable.interval(0, 1, TimeUnit.SECONDS)
                .observeOn(Schedulers.single())
                .map(count -> {
                    long timeBefore = SystemClock.elapsedRealtime();
                    InterpreterResult result1 = calcPrice1(points);
                    long timeAfter = SystemClock.elapsedRealtime();

                    InterpreterResult result2 = calcPrice2(points);
                    return new Result(result1, result2, count, timeAfter - timeBefore);
                })
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(compositePrice -> {
                    final CompositePrice emptyRouteCheck1 = PriceCalc.calculateBase(new ArrayList<>(), POLYGONS, PRICES_2);
                    final CompositePrice emptyRouteCheck2 = PriceCalc.calculateBase(new ArrayList<>(), POLYGONS_HELSINKI, PRICES_HELSINKI);
                    textView.setText("Result 1 : " + compositePrice.result1.getPrice().getTime() + "" +
                            "\nResult 1 : " + compositePrice.result2.getPrice().getTime() + "" +
                            "\ntime " + compositePrice.time + "" +
                            "\ncount " + compositePrice.count + "");
                });
    }

    private static class Result {
        long count;
        InterpreterResult result1;
        InterpreterResult result2;
        long time;

        public Result(InterpreterResult result1, InterpreterResult result2, long count, long time) {
            this.result1 = result1;
            this.result2 = result2;
            this.count = count;
            this.time = time;
        }
    }

    private InterpreterResult calcPrice1(ArrayList<MovementPoint> points) {
        final CompositePrice result1 = PriceCalc.calculateBase(points, POLYGONS, PRICES_1);
        return PriceCalc.runInterpreter(result1, TRIP_DETAILS, BYTECODE_return_price_x_0_9, 1);
    }

    private InterpreterResult calcPrice2(ArrayList<MovementPoint> points) {
        final CompositePrice result2 = PriceCalc.calculateBase(points, POLYGONS, PRICES_2);
        return PriceCalc.runInterpreter(result2, TRIP_DETAILS, BYTECODE_return_price_x_0_9, 1);
    }

    private ArrayList<MovementPoint> buildRandomTrack(int pointsCount) {
        ArrayList<MovementPoint> points = new ArrayList<>();
        double startLon = 4;
        double startLat = 5;
        double speed = 10;
        double distance = 5;
        Random random = new Random();
        for (int i = 0; i < pointsCount; i++) {
            double term = random.nextDouble();
            int plusOrMinus = startLat > 0 ? Double.compare(random.nextInt(), 0.5) : 1;
            startLat += term * plusOrMinus;
            startLon += term * plusOrMinus;
            speed += term * plusOrMinus;
            distance += term * plusOrMinus;
            MovementPoint point = new MovementPoint(startLon, startLat, distance, speed);
            points.add(point);
        }
        return points;
    }

    @Override
    public void onDestroyView() {
        disposable.dispose();
        super.onDestroyView();
    }
}
