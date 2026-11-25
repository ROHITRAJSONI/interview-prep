# JavaScript

## Q: Explain the event loop: microtasks vs macrotasks. What does this print?
```js
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve().then(() => console.log('C'));
console.log('D');
```
### Solution
Output: **A D C B**.

Synchronous code runs first (A, D). When the call stack empties, the engine drains the whole **microtask queue** (promise callbacks, `queueMicrotask`, MutationObserver), which prints C. Only then does it take the next **macrotask** (timers, I/O, UI events), which prints B. `await` is sugar over promises, so code after an `await` resumes as a microtask.

Practical point: a long synchronous loop, or endless chained microtasks, starves rendering and timers. Chunk the work or move it to a Web Worker.

## Q: What's the difference between `var`, `let`, `const`, and how does closure capture interact with loops?
### Solution
`var` is function-scoped and hoisted (initialized to `undefined`). `let`/`const` are block-scoped and in the temporal dead zone until they're declared. `const` prevents reassignment, not mutation of the object.

```js
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i)); // 3 3 3
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i)); // 0 1 2
```
With `var`, all three closures capture the same `i`. `let` creates a fresh binding per iteration. Default to `const`, use `let` when you need to reassign, and avoid `var`.
