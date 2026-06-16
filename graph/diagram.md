```mermaid
graph TD;
	__start__([<p>__start__</p>]):::first
	generate(generate)
	fact_check(fact_check)
	critique(critique)
	refine(refine)
	finalize(finalize)
	__end__([<p>__end__</p>]):::last
	__start__ --> generate;
	critique -.-> finalize;
	critique -.-> refine;
	fact_check --> critique;
	generate --> fact_check;
	refine --> fact_check;
	finalize --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```