"use strict";
function* __pipeline_perform__(__ctx__) {
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
      yield __fetch_args__;
      __rethrow_resource_fetch_exception__();
    } finally {
      __on_stage_exit__();
    }
  }
  {
    // [logic stage] stage1
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.stage1 = { status: 1 };
    let __stage_meta__ = __stages_meta__.stage1;
    try {
      __on_stage_enter__("stage1");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      for (let class_name in __ctx__.__resource__?.surge_experiment?.rules || {}) {
        let rule = __ctx__.__resource__?.surge_experiment?.rules[class_name];
        __stage_context__.class_name = class_name;
        // [in binding] access value
        let base_class = __ctx__.__resource__?.surge_zone?.base_class;
        const __tx_payload__ = (function(){
          __set_logging_region__("user_code", __stage_context__);
          // [logic stage] user code begin
// using class_name, rule and base_class here;
          // [logic stage] user code end
        })();
        if (typeof __tx_payload__ !== 'object') {
          throw 'returned "'+ typeof __tx_payload__ +'", but only "object" allowed. Value: ' + __tx_payload__;
        }
        if (__tx_payload__ !== null) {
          __set_logging_region__("out_bindings", __stage_context__);
          let stage_outs = new Set(['base_class_info']);
          for (let alias in __tx_payload__) {
            if (!stage_outs.has(alias)) {
              throw 'no out named "' + alias + '"';
            }
          }
          if (stage_outs.length > Object.keys(__tx_payload__).length) {
             throw 'expected more outputs than provided';
          }
          (function (__root_object__, __value_to_set__) {
            // [out binding] access value
            function __filter_matched_6__(__object_to_test__) {
              return __object_to_test__.name==base_class;
            }
            // check that new object itself satisfies conditions
            if (!__filter_matched_6__(__value_to_set__)) {
              throw "unable to push object to array: object doesn't satisfy filter condition;"
            }
            for (let __key7__ in __root_object__.classes) {
              let __value7__ = __root_object__.classes[__key7__];
              if (__filter_matched_6__(__value7__)) {
                // [out binding] assignment
                __root_object__.classes[__key7__] = __value_to_set__;
                return;
              }
            }
            // check that iterable is an array: search is allowed for objects
            // and arrays, but for objects failed search is an error because we
            // don't have a key
            if (!('push' in __root_object__.classes) || typeof __root_object__.classes.push !== 'function') {
              throw 'iterable search failed for object';
            }
            __root_object__.classes.push(__value_to_set__);
          })(__ctx__.__output__.__trx__, __tx_payload__['base_class_info']);
        }
        ++__stage_context__.__iteration_idx__;
        // set status "passed"
        __stage_meta__.status = 0;
      }
      // apply changes in output bindings
      __ctx__.__output__.__commit__();
    } finally {
      __on_stage_exit__();
    }
  }
  return {__sys__: __ctx__.__sys__};
}