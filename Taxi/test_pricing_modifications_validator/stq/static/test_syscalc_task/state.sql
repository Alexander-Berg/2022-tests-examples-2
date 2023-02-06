insert into db.script_tasks(id, script_body, var_constraints)
values (1, '', '{}');

insert into db.checks(id, script_id, check_type, message, check_body)
values (1, 1, 'CheckNaN', 'Message check', '; benchmark generated from python API
(set-info :status unknown)
(declare-sort AnyField 0)
 (declare-fun fix.discount.restrictions () AnyField)
(declare-fun is_initialized (AnyField) Bool)
(assert
 (and true))
(assert
 (let (($x18 (is_initialized fix.discount.restrictions)))
 (let (($x19 (= $x18 true)))
 (not $x19))))
(check-sat)
');
