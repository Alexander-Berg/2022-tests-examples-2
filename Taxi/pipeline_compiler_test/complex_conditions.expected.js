"use strict";
function* __pipeline_perform__(__ctx__) {
  // Intentionally do not store in __ctx__
  let __predicate_predicate_1__ = null;
  {
    // [predicate stage] predicate_1
    {
      let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
      // set status "omitted" by default
      __stages_meta__.predicate_1 = { status: 1 };
      let __stage_meta__ = __stages_meta__.predicate_1;
      __predicate_predicate_1__ = function(__stage_context__, arg1, arg2, arg3){
        __set_logging_region__("predicate_predicate_1", __stage_context__);
        // [predicate stage] user code begin
return {};
        // [predicate stage] user code end
      };
    }
  }
  // Intentionally do not store in __ctx__
  let __predicate_predicate_2__ = null;
  {
    // [predicate stage] predicate_2
    {
      let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
      // set status "omitted" by default
      __stages_meta__.predicate_2 = { status: 1 };
      let __stage_meta__ = __stages_meta__.predicate_2;
      __predicate_predicate_2__ = function(__stage_context__, arg4, arg5, arg6){
        __set_logging_region__("predicate_predicate_2", __stage_context__);
        // [predicate stage] user code begin
return {};
        // [predicate stage] user code end
      };
    }
  }
  // Intentionally do not store in __ctx__
  let __predicate_predicate_3__ = null;
  {
    // [predicate stage] predicate_3
    {
      let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
      // set status "omitted" by default
      __stages_meta__.predicate_3 = { status: 1 };
      let __stage_meta__ = __stages_meta__.predicate_3;
      __predicate_predicate_3__ = function(__stage_context__, ){
        __set_logging_region__("predicate_predicate_3", __stage_context__);
        // [predicate stage] user code begin
return {};
        // [predicate stage] user code end
      };
    }
  }
  // Intentionally do not store in __ctx__
  let __predicate_predicate_5__ = null;
  {
    // [predicate stage] predicate_5
    {
      let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
      // set status "omitted" by default
      __stages_meta__.predicate_5 = { status: 1 };
      let __stage_meta__ = __stages_meta__.predicate_5;
      __predicate_predicate_5__ = function(__stage_context__, ){
        __set_logging_region__("predicate_predicate_5", __stage_context__);
        // [predicate stage] user code begin
return {};
        // [predicate stage] user code end
      };
    }
  }
  // Intentionally do not store in __ctx__
  let __predicate_predicate_6__ = null;
  {
    // [predicate stage] predicate_6
    {
      let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
      // set status "omitted" by default
      __stages_meta__.predicate_6 = { status: 1 };
      let __stage_meta__ = __stages_meta__.predicate_6;
      __predicate_predicate_6__ = function(__stage_context__, ){
        __set_logging_region__("predicate_predicate_6", __stage_context__);
        // [predicate stage] user code begin
return {};
        // [predicate stage] user code end
      };
    }
  }
  {
    // [fetch stage] fetch_surge_zone
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.fetch_surge_zone = { status: 1 };
    let __stage_meta__ = __stages_meta__.fetch_surge_zone;
    try {
      __on_stage_enter__("fetch_surge_zone");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      let point = __ctx__.__input__?.point_a;
      const __fetch_args__ = (function(){
        __set_logging_region__("user_code", __stage_context__);
        // [fetch stage] user code begin
// using base_class and base_class_rule here;
return {
  surge_zone: {point: [0,0]},
  surge_experiment: {point: [0,0]},
};

        // [fetch stage] user code end
      })();
      __stage_meta__.status = 0;
      __set_logging_region__("native_code", __stage_context__);
      __fetch_resources__(__fetch_args__);
    } finally {
      __on_stage_exit__();
    }
  }
  {
    // [logic stage] logic_1
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.logic_1 = { status: 1 };
    let __stage_meta__ = __stages_meta__.logic_1;
    try {
      __on_stage_enter__("logic_1");
      let __stage_context__ = {__iteration_idx__: 0};
      if (__predicate_predicate_3__(__stage_context__, ) && (new Set([0,])).has(__stages_meta__.fetch_surge_zone.status)) {
        // [in binding] access value
        for (let val1 in __ctx__.__input__?.query?.step || {}) {
          let __value5__ = __ctx__.__input__?.query?.step[val1];
          __stage_context__.val1 = val1;
          let val2 = __value5__?.nested?.two;
          let val3 = __value5__?.nested?.three;
          if (__predicate_predicate_1__(__stage_context__, val1, val2, val3)) {
            for (let val5 in __value5__?.nested?.deep || {}) {
              let __value7__ = __value5__?.nested?.deep[val5];
              __stage_context__.val5 = val5;
              let val4 = __value7__?.even?.four;
              let val6 = __value7__?.even?.six;
              if (__predicate_predicate_2__(__stage_context__, val4, val5, val6)) {
                for (let very in __value7__?.even?.more?.deep || {}) {
                  let important = __value7__?.even?.more?.deep[very];
                  __stage_context__.very = very;
                  const __tx_payload__ = (function(){
                    __set_logging_region__("user_code", __stage_context__);
                    // [logic stage] user code begin
return {}
                    // [logic stage] user code end
                  })();
                  if (typeof __tx_payload__ !== 'object') {
                    throw 'returned "'+ typeof __tx_payload__ +'", but only "object" allowed. Value: ' + __tx_payload__;
                  }
                  ++__stage_context__.__iteration_idx__;
                  // set status "passed"
                  __stage_meta__.status = 0;
                }
              }
            }
          }
        }
      }
      // apply changes in output bindings
      __ctx__.__output__.__commit__();
    } catch (error) {
      log.error("Stage failed: " + error);
      // set status "failed"
      __stage_meta__.status = 2;
      __stage_meta__.error = error;
      // set proper error type for stats
      __stage_meta__.error_type = error.__ytx_custom_error_type__ || null;
      // reset changes in output bindings
      __ctx__.__output__.__rollback__();
    } finally {
      __on_stage_exit__();
    }
  }
  {
    // [logic stage] logic_2
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.logic_2 = { status: 1 };
    let __stage_meta__ = __stages_meta__.logic_2;
    try {
      __on_stage_enter__("logic_2");
      let __stage_context__ = {__iteration_idx__: 0};
      if ((__predicate_predicate_5__(__stage_context__, ) || (__predicate_predicate_6__(__stage_context__, ) && !__predicate_predicate_3__(__stage_context__, )) || __predicate_predicate_3__(__stage_context__, ) || ((new Set([0,])).has(__stages_meta__.fetch_surge_zone.status) || !__predicate_predicate_6__(__stage_context__, )))) {
        const __tx_payload__ = (function(){
          __set_logging_region__("user_code", __stage_context__);
          // [logic stage] user code begin
return {}
          // [logic stage] user code end
        })();
        if (typeof __tx_payload__ !== 'object') {
          throw 'returned "'+ typeof __tx_payload__ +'", but only "object" allowed. Value: ' + __tx_payload__;
        }
        ++__stage_context__.__iteration_idx__;
        // set status "passed"
        __stage_meta__.status = 0;
      }
      // apply changes in output bindings
      __ctx__.__output__.__commit__();
    } catch (error) {
      log.error("Stage failed: " + error);
      // set status "failed"
      __stage_meta__.status = 2;
      __stage_meta__.error = error;
      // set proper error type for stats
      __stage_meta__.error_type = error.__ytx_custom_error_type__ || null;
      // reset changes in output bindings
      __ctx__.__output__.__rollback__();
    } finally {
      __on_stage_exit__();
    }
  }
  return {__sys__: __ctx__.__sys__};
}