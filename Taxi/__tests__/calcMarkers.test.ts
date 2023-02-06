import {calcMarkers} from '../calcMarkers';

describe('calcMarkers', () => {
    test('pricing source code diff without ending line break', () => {
        const originValue =
            `"function max(a:double, b:double) {
              return { res = (a > b) ? a : b };
            }

            // Коэффициент максимально разрешённого тарифа
            let mrt_coeff = (fix.base_price_discount as bpd) ? bpd.boarding_discount : 1;

            // Минимальная цена = [максимум из посадки и минимальной цены в тарифе] * [коэффициент МРТ]
            let minimum = max(a=fix.tariff.boarding_price, b=fix.tariff.minimum_price).res * mrt_coeff;

            if (ride.price.boarding + ride.price.distance + ride.price.time < minimum) {
              return {
                boarding = minimum - ride.price.distance - ride.price.time
              };
            }
            return ride.price;"`;

        const newValue =
            `"function max(a:double, b:double) {
              return { res = (a > b) ? a : b };
            }

            // Коэффициент максимально разрешённого тарифа
            let mrt_coeff = (fix.base_price_discount as bpd) ? bpd.boarding_discount : 1;

            // Минимальная цена = [максимум из посадки и минимальной цены в тарифе] * [коэффициент МРТ]
            let minimum = max(a=fix.tariff.boarding_price, b=fix.tariff.minimum_price).res * mrt_coeff;

            let delta = (ride.price.boarding + ride.price.distance + ride.price.time < minimum)
                          ? minimum - (ride.price.boarding + ride.price.distance + ride.price.time)
                          : 0;


            return {
              boarding = ride.price.boarding + delta
            };
            "`;
        const {valueWithDiff, markers} = calcMarkers(originValue, newValue);

        const res =
        `"function max(a:double, b:double) {
              return { res = (a > b) ? a : b };
            }

            // Коэффициент максимально разрешённого тарифа
            let mrt_coeff = (fix.base_price_discount as bpd) ? bpd.boarding_discount : 1;

            // Минимальная цена = [максимум из посадки и минимальной цены в тарифе] * [коэффициент МРТ]
            let minimum = max(a=fix.tariff.boarding_price, b=fix.tariff.minimum_price).res * mrt_coeff;

            if (ride.price.boarding + ride.price.distance + ride.price.time < minimum) {
              return {
                boarding = minimum - ride.price.distance - ride.price.time
              };
            }
            return ride.price;"
            let delta = (ride.price.boarding + ride.price.distance + ride.price.time < minimum)
                          ? minimum - (ride.price.boarding + ride.price.distance + ride.price.time)
                          : 0;


            return {
              boarding = ride.price.boarding + delta
            };
            "\n`;
        const removed = markers[0];
        const added = markers[1];
        expect(valueWithDiff).toEqual(res);
        expect(removed.startRow).toEqual(10);
        expect(removed.endRow).toEqual(15);
        expect(added.startRow).toEqual(16);
        expect(added.endRow).toEqual(24);
    });

});
