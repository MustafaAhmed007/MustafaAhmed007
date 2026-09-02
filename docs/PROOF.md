# Proof Registry

This file is the canonical template for adding public evidence without turning the profile into a claim list.

## Evidence ladder

Prefer the strongest available artifact:

1. **Shipped implementation** — public repository with usable code.
2. **Live artifact** — deployed product, demo, or working interface.
3. **Measured result** — benchmark, test result, operational metric, or before/after measurement with reproducible context.
4. **Case study** — problem, approach, implementation, outcome, and constraints.
5. **Technical write-up** — architecture or implementation explanation linked to an artifact.

## Project entry template

```yaml
name: "Project name"
type: "SYSTEM | PRODUCT | TOOL | AUTOMATION"
problem: "Specific problem solved"
built: "What was actually implemented"
outcome: "Observed result or shipped state"
repo: "https://github.com/your-username/project"
status: "SHIPPED | ACTIVE | EXPERIMENT"
```

## Publishing rule

Do not add a capability to the public profile merely because it is planned or studied. Add it when there is inspectable evidence, then strengthen the entry as stronger evidence becomes available.

## Evidence loop

```text
Build → ship → document → link → measure → improve → repeat
```
