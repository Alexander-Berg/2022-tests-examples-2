$script = @@
import hashlib
import sys
import datetime

def exp3_hash(arg, salt):
    sha1 = hashlib.sha1()
    sha1.update(salt)
    sha1.update(arg)
    res = sha1.hexdigest()[:16]
    return int(res, 16)%100
@@;

$exp_flg = Python::exp3_hash(Callable<(String?, String?) -> Int64?>, $script);
$salt = 'global_test_control_demand_202107';
$exp_group = ($x) -> {

$result = $exp_flg($x, $salt);
Return case when $result between 0 and 87 then 'exp_user'
            when $result between 88 and 93 then 'global_test'
            when $result between 94 and 99 then 'global_control'
        else 'other' end
};