# ADR 0001: shared tools before a vehicle architecture

Status: accepted for this starter workspace; club review invited.

## Context

Project interests span several vehicle types. No hardware, onboard processor, telemetry transport, or operating site has been selected. Prematurely choosing a firmware stack or flight architecture would create unsupported constraints.

## Decision

Keep one repository for shared offline tools and engineering practice. Use Python's standard library for a small inspectable telemetry validator. Define an exported CSV/JSON analysis boundary with explicit units and provenance. Keep hardware adapters, control software, dashboards, and mission simulations out until there is a specific requirement and a way to validate them.

## Alternatives and consequences

A notebook-first approach is convenient for exploration but makes repeatable validation less obvious to new contributors. A large scientific stack supports plotting and numerical methods but is unnecessary for the current tool. Revisit either when a real analysis needs it.

The strict synchronized CSV format deliberately rejects missing values and asynchronous channels. This makes assumptions visible, but future devices will need adapters or a separate stream-oriented contract. Preserve native logs so this decision remains reversible.

The project has no package publishing workflow. Run tools from the repository root; add packaging only when another project needs installation. Tests verify software contracts, not sensor performance.

## Revisit when

A selected project supplies representative public-safe data, a documented clock model, or an integration requirement the current contract cannot express.
