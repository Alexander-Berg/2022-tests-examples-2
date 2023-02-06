const route_point_info = order_context.route_point_info;
if (route_point_info == undefined) {
    return 300;
}
if (route_point_info.length != 1) {
    return 0;
}
if (route_point_info[0].is_airport) {
    trace.text = 'airport'
    return 100;
}
return 200;
