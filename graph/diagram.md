```mermaid
graph TD;
	__start__([<p>__start__</p>]):::first
	guard_input(guard_input)
	blocked(blocked)
	detect_skill(detect_skill)
	generate(generate)
	fact_check(fact_check)
	critique(critique)
	critique_code(critique_code)
	refine(refine)
	track_best(track_best)
	finalize(finalize)
	__end__([<p>__end__</p>]):::last
	__start__ --> guard_input;
	critique --> track_best;
	critique_code --> track_best;
	detect_skill --> generate;
	fact_check -.-> critique;
	fact_check -.-> critique_code;
	generate --> fact_check;
	guard_input -.-> blocked;
	guard_input -.-> detect_skill;
	refine --> fact_check;
	track_best -.-> finalize;
	track_best -.-> refine;
	blocked --> __end__;
	finalize --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```