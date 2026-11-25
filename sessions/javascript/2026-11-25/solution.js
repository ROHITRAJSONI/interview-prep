'use strict';

/**
 * Run async task factories with at most `limit` in flight.
 * Results keep input order; rejects on first failure (fail-fast) and
 * stops starting new tasks.
 */
function promisePool(tasks, limit) {
  if (!Number.isInteger(limit) || limit < 1) {
    return Promise.reject(new RangeError('limit must be a positive integer'));
  }
  return new Promise((resolve, reject) => {
    const results = new Array(tasks.length);
    let next = 0;
    let done = 0;
    let failed = false;
    if (tasks.length === 0) return resolve(results);

    const launch = () => {
      if (failed || next >= tasks.length) return;
      const i = next++;
      Promise.resolve()
        .then(() => tasks[i]())          // sync throws become rejections
        .then(value => {
          results[i] = value;
          if (++done === tasks.length) resolve(results);
          else launch();                 // refill the freed slot
        }, err => {
          failed = true;
          reject(err);
        });
    };
    for (let k = 0; k < Math.min(limit, tasks.length); k++) launch();
  });
}

module.exports = { promisePool };

// ---- demo / self-test ----
if (require.main === module) {
  const sleep = (ms, v) => new Promise(r => setTimeout(() => r(v), ms));
  let running = 0, peak = 0;
  const mk = (id, ms) => async () => {
    running++; peak = Math.max(peak, running);
    await sleep(ms); running--; return id;
  };
  (async () => {
    const out = await promisePool([mk('a', 50), mk('b', 10), mk('c', 20), mk('d', 5), mk('e', 15)], 2);
    console.assert(JSON.stringify(out) === '["a","b","c","d","e"]', 'order');
    console.assert(peak === 2, 'peak concurrency ' + peak);
    console.log('results', out, 'peak', peak);
    try { await promisePool([() => sleep(5), () => { throw new Error('boom'); }], 2); }
    catch (e) { console.log('rejected:', e.message); }
  })();
}
