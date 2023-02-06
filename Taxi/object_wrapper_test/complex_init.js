function test(ctx) {
  let e0 = ctx.empty_1.__trx__;
  e0.one = ctx.empty.one;
  let e1 = ctx.empty_2.__trx__;
  e1.one = ctx.empty_1.one;
  ctx.__commit__();

  let f0 = ctx.filled_1.__trx__;
  f0.one = ctx.filled.one;
  let f1 = ctx.filled_2.__trx__;
  f1.one = ctx.filled_1.one;
  ctx.__commit__();

  return 'ok';
}
