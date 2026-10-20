# Detector and synthetic-data contract

By Jason Stys. These are inspectable statistical heuristics, not physical spacecraft models or operational health determinations.

## Data and training boundary

Frames have consecutive integer ticks, characterized mode SUNLIT/ECLIPSE and three values: thermal, bus and load. Each channel value is finite within ±10,000, or absent (`None` / JSON null / CSV blank). Flags, infinities, NaN, unknown modes, wrong arity and reordered ticks are refused. Supported runs have 240 or 480 frames; the fixed training prefix is ticks 0–79.

Training must contain every channel and at least 12 frames of each characterized context. The prefix is **assumed clean**, not certified clean. There is no test-label-driven removal of anomalous training points. A contaminated or nonrepresentative prefix can produce bad limits. No baseline adapts from evaluation data.

For each channel and, optionally, each context:

```text
center = median(training values)
MAD = median(abs(value - center))
scale = max(1, 1.4826 × MAD)
point limits = center ± multiplier × scale
```

NIST describes MAD as a robust scale estimate; the conventional normal-consistency factor does not make a threshold a probability or calibrated confidence interval. The unit floor is an explicit teaching safeguard for constant/quantized signals, not a physical sensor calibration. [NIST MAD](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/mad.htm).

The context-aware model fits two bands per channel; the pooled comparison mixes both modes. Both use the exact same training/evaluation split. Because mode proportions and centers differ, a pooled median/MAD model can flag entirely legitimate mode changes. This illustrates why model context matters; it is not a claim that this particular algorithm outperforms all alternatives on real telemetry.

## Causal scoring order

The detector receives only one observation at a time starting at tick 80. It has no truth-label argument. It requires consecutive post-training frames. On context change it resets temporal state for all channels; on a missing observation it resets only the affected channel. It never substitutes zero, carries a measurement forward or invents an observation.

For a present value, in order:

1. Select its frozen band and compute signed residual `z = (value − center) / scale`.
2. Update `EWMA = 0.2 × z + 0.8 × previous_EWMA` (initially zero).
3. Increment exact-equality run length, or reset length to one for a changed reading.
4. Flag `point-limit` when `abs(z) > multiplier`; `drift` when `abs(EWMA) > 0.6 × multiplier`; `flatline` when the run length is at least six.

Flags can coexist. Comparisons are strict `>`; a residual exactly at the point limit does not trigger that rule. Reports round residual, EWMA and bounds to six decimals only after the decision; calculations retain native float precision. Equality-based flatline is appropriate to this intentionally quantized teaching stream, not a universal stuck-sensor detector. Context resets can delay a real persistent-fault detection. EWMA memory can continue flagging after a fault ends, producing false positives; those are counted, not hidden.

## Synthetic generator

A fixed 32-bit linear congruential generator (`state = (1664525 × state + 1013904223) mod 2^32`) adds an integer noise value from −4 to +4 to invented channel centers. Seed choices are 7, 23, 101. This is reproducible test data, not cryptographic randomness or a realistic spacecraft simulation.

SUNLIT applies when `tick % 40 < 24`, otherwise ECLIPSE. Centers are (500,780,250) and (390,750,180). Ticks are not seconds; names are context categories, not a thermal/electrical/orbit model.

| Fixture            | Injection at selected fault tick (120 or160)   |
| ------------------ | ---------------------------------------------- |
| nominal            | No injected sensor anomaly                     |
| isolated-spike     | Add40 to one thermal observation               |
| multichannel-burst | Bus−28 and load+32 for12 ticks                 |
| slow-drift         | Thermal bias +1 through +36 over36 ticks       |
| stuck-sensor       | Freeze the initial thermal reading for36 ticks |
| telemetry-gap      | All3 channel values absent for12 ticks         |
| partial-dropout    | Only bus absent for12 ticks                    |
| step-shift         | Thermal+24 for36 ticks                         |

All injections occur after training. Truth labels are held separately from observations, never passed to training/scoring, and used only by the post-scoring evaluator. Missing-data fixtures are quality issues, not positively labeled sensor anomalies. Even a numerical fault's first few biased observations may look normal: labels represent the known injected interval, not an artificially delayed label chosen to boost recall.

## Evaluation semantics

The unit is an **observed evaluation channel-tick**, not a packet, event or spacecraft failure. TP/FP/FN/TN exclude training and absent readings. `precision=TP/(TP+FP)`, `recall=TP/(TP+FN)`, `F1=2TP/(2TP+FP+FN)`. A zero denominator is null/Undefined, not0 or100%. Absence counts separately. Detection delay is the first observed true-positive tick minus the first observed injected-positive tick in these single-injection fixtures; no true positive means undefined. It is not a general multi-event latency statistic.

Local CSV imports have no truth labels; confusion counts, precision/recall/F1/delay remain null. Observed/missing/alert counts still describe the actual scoring output. Synthetic benchmark scores must not be presented as real-mission effectiveness or safety evidence.

## Complexity

For N training frames, T evaluation frames, C channels and M contexts, median/MAD fitting is O(CN log N + MN) with ordinary sorted medians; two tiny context scans are explicit. Scoring is O(TC), with O(C) mutable temporal state plus O(MC) frozen bands. Complete observation/report/comparison storage, hashing and export are O((N+T)C); there is no claim that the returned full report is constant-memory streaming. Browser drawing is O((N+T)C) per channel redraw and O(1) per tick inspection. The serialized cache holds at most24 finite synthetic results; callers receive detached copies. Limits of480 frames/3 channels keep the teaching workload bounded. These are algorithmic costs, not hard real-time or throughput guarantees.
