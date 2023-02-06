"use strict";
function* __pipeline_perform__(__ctx__) {
  {
    // [fetch stage] stage1
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.stage1 = { status: 1 };
    let __stage_meta__ = __stages_meta__.stage1;
    try {
      __on_stage_enter__("stage1");
      let __stage_context__ = {__iteration_idx__: 0};
      const __fetch_args__ = (function(){
        __set_logging_region__("user_code", __stage_context__);
        // [fetch stage] user code begin

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
    // [fetch stage] stage2
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.stage2 = { status: 1 };
    let __stage_meta__ = __stages_meta__.stage2;
    try {
      __on_stage_enter__("stage2");
      let __stage_context__ = {__iteration_idx__: 0};
      const __fetch_args__ = (function(){
        __set_logging_region__("user_code", __stage_context__);
        // [fetch stage] user code begin

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
    // [fetch stage] stage3
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.stage3 = { status: 1 };
    let __stage_meta__ = __stages_meta__.stage3;
    try {
      __on_stage_enter__("stage3");
      let __stage_context__ = {__iteration_idx__: 0};
      const __fetch_args__ = (function(){
        __set_logging_region__("user_code", __stage_context__);
        // [fetch stage] user code begin

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
    // [logic stage] stage4
    let __stages_meta__ = __ctx__.__sys__.__stages_meta__;
    // set status "omitted" by default
    __stages_meta__.stage4 = { status: 1 };
    let __stage_meta__ = __stages_meta__.stage4;
    try {
      __on_stage_enter__("stage4");
      let __stage_context__ = {__iteration_idx__: 0};
      // [in binding] access value
      let resource = __ctx__.__resource__?.resource;
      const __tx_payload__ = (function(){
        __set_logging_region__("user_code", __stage_context__);
        // [logic stage] user code begin
result = resource + resource + resource
        // [logic stage] user code end
      })();
      if (typeof __tx_payload__ !== 'object') {
        throw 'returned "'+ typeof __tx_payload__ +'", but only "object" allowed. Value: ' + __tx_payload__;
      }
      if (__tx_payload__ !== null) {
        __set_logging_region__("out_bindings", __stage_context__);
        let stage_outs = new Set(['result']);
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
          // [out binding] assignment
          __root_object__.result = __value_to_set__;
          return;
        })(__ctx__.__output__.__trx__, __tx_payload__['result']);
      }
      ++__stage_context__.__iteration_idx__;
      // set status "passed"
      __stage_meta__.status = 0;
      // apply changes in output bindings
      __ctx__.__output__.__commit__();
    } finally {
      __on_stage_exit__();
    }
  }
  return {__sys__: __ctx__.__sys__};
}