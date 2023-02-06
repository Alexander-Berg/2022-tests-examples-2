let c1 = place_settings.c1;
let c2 = place_settings.c2;

for (let i = 0; i < 3; i++) {
  let l = 100 * (c2[i] + (c1[i] / (free + busy)));
  log.info('l[' + i + '] = ' + l);
  if (load_level < l) return {surge_level: i};
}
return {surge_level: 3};
