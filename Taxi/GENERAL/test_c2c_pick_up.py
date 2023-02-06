from library.mocks.c2c_bodies import C2C_CREATE_OFFER_BODY
from library.c2c_request import c2c_create_request, c2c_get_pick_up_points,c2c_change_stations_payload, c2c_confirm_request,c2c_create_request_without_err
import time
import random


# There isn't test. It's function to get list of id's  stations
# True to get availible dropoffs stations
def c2c_get_list_drop_off(drop_off):
    result = c2c_get_pick_up_points(drop_off)
    print(len(result))
    return result

# Return exception in case of any problem
def test_c2c_create_and_confirm(src =  None, dstn = None):
    if src == None and dstn == None:
        body = C2C_CREATE_OFFER_BODY
    else:
        body = c2c_change_stations_payload(C2C_CREATE_OFFER_BODY, src, dstn)
    result_create = c2c_create_request_without_err(C2C_CREATE_OFFER_BODY)
    result  = c2c_confirm_request(body, result_create['offers'][0]['offer_id'])
    print(result)
    assert len(result) > 0


# Return exception in case of any problem
def test_c2c_create_offer():
    result = c2c_create_request(C2C_CREATE_OFFER_BODY)
# combination of options to make delivery
# mode None is default, check all available combinations
# mode 1 meam onerandom combination
# mode 20 mean 20 percent random stations
def test_c2c_check_all_routes(mode = None):
    cnt_ok = 0 
    cnt_err = 0 
    start_points = []
    end_points = []
    if (mode == None):
       start_points = c2c_get_list_drop_off(True)
       end_points = c2c_get_list_drop_off(False)
    elif (mode == 1):
        start_points = random.choices(c2c_get_list_drop_off(True), k = 1)
        end_points = random.choices(c2c_get_list_drop_off(False), k = 1)
    else:
        start_points = random.choices(c2c_get_list_drop_off(True), k = round(len(c2c_get_list_drop_off(True)) * 20 / 100))
        end_points = random.choices(c2c_get_list_drop_off(False), k = round(len(c2c_get_list_drop_off(False)) * 20 / 100))
    print(start_points)
    print(end_points)
    for a in range(len(start_points)):
        for b in range(len(end_points)):
            time.sleep(1)
            try:
                test_c2c_create_and_confirm(src =  start_points[a], dstn = end_points[b])
                cnt_ok = cnt_ok + 1
            except Exception as err:
                print("For source "+start_points[a]+" and destination " + end_points[b] +" ERROR_REASON ")
                print(err)
                cnt_err = cnt_err + 1
                #break
                continue
    print("cnt_ok = " + str(cnt_ok) + " cnt_err "+ str(cnt_err))

if __name__ == '__main__':
    #test_c2c_check_all_routes()
    #c2c_get_list_drop_off(False)
    test_c2c_create_offer()
    #test_c2c_create_and_confirm()