"""Deterministic worked-example functions for
"No-Harm Principles in AI Architectures: Ahimsa-Driven Multi-Agent AI
Systems" by Dr. Sri Amit Ray (Compassionate AI Lab, 2026).
ISBN 978-81-69641-30-2 (First Edition, 2026).

Every function is pure and reproducible: no randomness, no network, no
wall-clock inputs. The worked examples in the book quote these outputs.
The input values are small illustrative numbers chosen to show the
reasoning pattern of each chapter; replace them with your own measured
values before using any function for planning.

Run:   python models_no_harm_principles_in_ai_architectures.py
Test:  python -m unittest test_models.py
"""
from __future__ import annotations

import hashlib
import math


def _finite(x, lo=None):
    """True for a real, finite number (bool excluded) not below lo."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    if not math.isfinite(x):
        return False
    return lo is None or x >= lo


# ---------------------------------------------------------------- ch01
def ch01_emergent_risk(p_local=0.04, rho=0.18, density=6.0,
                       safe_density=3.0, amp_per_excess=1.35):
    """Corridor collision screen for a pair of drones sharing signals.

    rho is a shared-cause coupling coefficient used by the screen
    p^2 + rho*p.  It is a conservative screening value, not a measured
    collision probability: if rho were the Pearson correlation of two
    equal-probability binary failures, the exact joint probability
    would be p^2 + rho*p*(1 - p) (see ch01_pearson_joint).

    Returns (independent pair value p^2, correlated pair screen
    p^2 + rho*p, amplification allowance A, corridor hazard
    P_joint * (1 + A)).
    """
    indep = round(p_local * p_local, 4)
    joint = p_local * p_local + rho * p_local
    excess = max(0.0, density - safe_density)
    corridor_amp = amp_per_excess * excess
    hazard = round(joint * (1.0 + corridor_amp), 4)
    return indep, round(joint, 4), round(corridor_amp, 2), hazard


def ch01_pearson_joint(p_local=0.04, rho=0.18):
    """Exact joint failure probability when rho is the Pearson
    correlation of two Bernoulli(p) failures: p^2 + rho*p*(1-p)."""
    return round(p_local * p_local + rho * p_local * (1.0 - p_local), 6)


def ch01_chain_handoff(local_err=0.03, handoffs=4):
    """Probability that a chain of handoffs stays clean, and its complement."""
    p_clean = (1.0 - local_err) ** handoffs
    return round(p_clean, 4), round(1.0 - p_clean, 4)


def ch01_harm_screen(severity=4, prob=0.0088, exposure=3, uncert=1.5):
    """Illustrative multiplicative risk screen R = S * P * E * U."""
    return round(severity * prob * exposure * uncert, 4)


# ---------------------------------------------------------------- ch02
def ch02_least_harm_option(pi_max=1.5):
    """Feasibility before reward: harm index pi = S * rho_irr.

    Options with pi above pi_max are inadmissible.  Among admissible
    options the least harmful one is chosen; the option a pure utility
    maximiser would pick is returned for comparison.
    Returns (scored, admissible, chosen, utility_pick).
    """
    opts = [("A", 4, 0.9, 1.30), ("B", 2, 0.7, 2.10),
            ("C", 3, 0.4, 1.90), ("D", 1, 0.2, 1.70)]
    scored = {name: {"pi": round(s * r, 2), "severity": s, "rho": r,
                     "utility": u} for name, s, r, u in opts}
    admissible = [n for n, v in scored.items() if v["pi"] <= pi_max]
    chosen = min(admissible, key=lambda n: (scored[n]["pi"], -scored[n]["utility"]))
    utility_pick = max(scored, key=lambda n: scored[n]["utility"])
    return scored, admissible, chosen, utility_pick


# ---------------------------------------------------------------- ch03
def ch03_floor_coverage(e, c):
    """Floor coverage: share of floors enforced at the collective level.

    e[i] = 1 if floor i has an existing constraint, c[i] = 1 if it is
    enforced on joint actions.  Returns (covered, total, coverage, gaps).
    """
    n = len(e)
    covered = sum(1 for x, y in zip(e, c) if x and y)
    gaps = [i for i, (x, y) in enumerate(zip(e, c)) if not (x and y)]
    return covered, n, covered / n, gaps


FLOORS = ["consent", "non-discrimination", "physical safety envelope",
          "no unauthorized disclosure", "protection of neglected groups",
          "escalation of unresolved collective risk", "contestability",
          "high-integrity audit"]
FLOOR_E = [1, 1, 1, 1, 1, 1, 1, 1]
FLOOR_C = [1, 0, 1, 1, 0, 1, 0, 1]


# ---------------------------------------------------------------- ch04
INTERACTION = {(1, 1): 0.30, (1, 2): 0.55, (1, 3): 0.20,
               (2, 1): 0.28, (2, 2): 0.42, (2, 3): 0.25}


def ch04_joint_feasibility(xi=0.40):
    """Two agents, three slots: product of local sets versus A_CF.

    Returns (|product|, |A_CF|, violators, greedy pair, greedy utility,
    best feasible pair, best feasible utility).
    """
    hx, hy = (0.20, 0.08, 0.35), (0.10, 0.25, 0.05)
    ex = ey = 0.30
    ux, uy = (0.90, 0.75, 0.40), (0.60, 0.80, 0.50)
    local_x = [i + 1 for i, h in enumerate(hx) if h <= ex]
    local_y = [j + 1 for j, h in enumerate(hy) if h <= ey]
    product = [(x, y) for x in local_x for y in local_y]
    feasible = [k for k in product if INTERACTION[k] <= xi]
    violators = [k for k in product if INTERACTION[k] > xi]

    def util(k):
        return ux[k[0] - 1] + uy[k[1] - 1]

    greedy = max(product, key=util)
    best = max(feasible, key=util)
    return (len(product), len(feasible), violators,
            greedy, round(util(greedy), 2), best, round(util(best), 2))


ESCALATE = "ESCALATE"


def collective_filter(proposals, local_ok, collective_harm, xi, utility,
                      uncertainty=None, tolerance=None, gates_ok=None):
    """Collective Feasibility Filter (Algorithm 4.1).

    proposals       iterable of joint actions
    local_ok(a)     True if every agent's own constraint holds for a
    collective_harm(a) -> projected collective harm of a
    xi              system-level bound (finite, >= 0)
    utility(a)      summed reward, consulted only inside A_CF
    uncertainty(a)  optional: uncertainty of the harm estimate
    tolerance       largest uncertainty accepted (needed with uncertainty)
    gates_ok(a)     optional: True if a is authorized and every required
                    consent is given (Section 4.2); default: no gates

    Unknown risk is never a pass (Axiom 3): a harm estimate that raises,
    is None, NaN, infinite, negative or not a number, or whose
    uncertainty is unknown or above tolerance, is logged "unresolved".
    Returns (chosen joint action, or ESCALATE if A_CF is empty,
    A_CF, rejected with reasons).
    """
    if not _finite(xi, 0.0):
        raise ValueError("xi must be a finite, non-negative number")
    if uncertainty is not None and not _finite(tolerance, 0.0):
        raise ValueError("tolerance must be finite and non-negative")
    a_cf, rejected = [], []
    for a in proposals:
        if gates_ok is not None and gates_ok(a) is not True:
            rejected.append((a, "gate"))
            continue
        if local_ok(a) is not True:
            rejected.append((a, "individual"))
            continue
        try:
            h = collective_harm(a)
        except Exception:
            h = None
        if not _finite(h, 0.0):
            rejected.append((a, "unresolved"))
            continue
        if uncertainty is not None:
            try:
                u = uncertainty(a)
            except Exception:
                u = None
            if not _finite(u, 0.0) or u > tolerance:
                rejected.append((a, "unresolved"))
                continue
        if h > xi:
            rejected.append((a, "collective"))
        else:
            a_cf.append(a)
    chosen = max(a_cf, key=utility) if a_cf else ESCALATE
    return chosen, a_cf, rejected


# ---------------------------------------------------------------- ch05
def _pure_nash(payoff, strategies):
    """All pure-strategy Nash equilibria of a two-player game."""
    eq = []
    for a in strategies:
        for b in strategies:
            ua, ub = payoff[(a, b)]
            if all(payoff[(x, b)][0] <= ua for x in strategies) and \
               all(payoff[(a, y)][1] <= ub for y in strategies):
                eq.append((a, b))
    return eq


def ch05_floor_game():
    """Prisoner's dilemma; then the harmful defection removed by a floor.

    Returns (equilibria and payoff of the unconstrained game,
             of the game with all defection floored,
             of the game where only severe defection is floored).
    """
    base = {("C", "C"): (3.0, 3.0), ("C", "D"): (0.0, 5.0),
            ("D", "C"): (5.0, 0.0), ("D", "D"): (1.0, 1.0)}
    eq0 = _pure_nash(base, ["C", "D"])
    eq1 = _pure_nash(base, ["C"])
    mild = {("C", "C"): (3.0, 3.0), ("C", "Dm"): (0.6, 4.5),
            ("Dm", "C"): (4.5, 0.6), ("Dm", "Dm"): (2.2, 2.2)}
    eq2 = _pure_nash(mild, ["C", "Dm"])
    return ((eq0, base[eq0[0]]), (eq1, base[eq1[0]]), (eq2, mild[eq2[0]]))


# ---------------------------------------------------------------- ch06
H6 = (0.00, 0.05, 0.10, 0.00, 0.02, 0.15)
W6 = (1.0, 1.0, 1.0, 1.0, 1.0, 1.5)
VULNERABLE_STEPS = {5}


def ch06_trajectory_harm(gam=0.9):
    """Severity-weighted trajectory harm: discounted, undiscounted, and
    discounted with a vulnerability floor (no discount on steps that touch
    a declared vulnerable population)."""
    disc = sum((gam ** t) * W6[t] * H6[t] for t in range(6))
    plain = sum(W6[t] * H6[t] for t in range(6))
    floored = sum((1.0 if t in VULNERABLE_STEPS else gam ** t) * W6[t] * H6[t]
                  for t in range(6))
    return round(disc, 4), round(plain, 4), round(floored, 4)


def ch06_early_escalation(h=(0.04, 0.07, 0.10, 0.13), xi=0.60, review_in=3):
    """Rate-of-accumulation trigger: escalate when the running total plus
    the current slope times the steps until the next human review would
    cross the bound.  Returns (running totals, step of escalation or None,
    step at which the total itself would cross, or None if the trend
    never crosses).  The extrapolation stops as soon as the increments
    stop growing the total, so a flat or falling trajectory ends."""
    if not _finite(xi) or not isinstance(review_in, int) or review_in < 0:
        raise ValueError("xi must be finite and review_in an int >= 0")
    if not all(_finite(x) for x in h):
        raise ValueError("increments must be finite numbers")
    if not h:
        return [], None, None
    total, totals, esc = 0.0, [], None
    for t, x in enumerate(h):
        total += x
        totals.append(round(total, 3))
        slope = x - h[t - 1] if t else x
        projected = total + sum(x + slope * (k + 1) for k in range(review_in))
        if esc is None and projected > xi:
            esc = t + 1
    cross, run = None, 0.0
    for t, x in enumerate(h):
        run += x
        if run > xi:
            cross = t + 1
            break
    if cross is None:          # extrapolate the same slope
        run, x, t = sum(h), h[-1], len(h)
        slope = h[-1] - h[-2] if len(h) > 1 else h[-1]
        while run <= xi:
            x += slope
            if x <= 0 and slope <= 0:      # total can never grow again
                return totals, esc, None
            run += x
            t += 1
            if t > 100000:                 # safety cap
                return totals, esc, None
        cross = t
    return totals, esc, cross


# ---------------------------------------------------------------- ch07
ENVELOPE_FIELDS = ["task_id", "sender", "recipient", "action_proposal",
                   "assumptions", "uncertainty", "authorization_scope",
                   "safety_status"]
LADDER = ["reformulate", "staged_commitment", "escalate", "refuse"]
SAFETY_STATUSES = ("green", "yellow", "red")
GATE_CRITICAL = ("uncertainty", "authorization_scope", "safety_status")


def _text(v):
    return isinstance(v, str) and v.strip() != ""


def _text_or_list(v):
    if _text(v):
        return True
    return isinstance(v, (list, tuple)) and len(v) > 0 and all(_text(x) for x in v)


def _uncertainty_ok(v):
    """A finite number >= 0, a [low, high] range, or a non-empty dict
    mapping each harm dimension to one of those."""
    def one(x):
        if _finite(x, 0.0):
            return True
        return (isinstance(x, (list, tuple)) and len(x) == 2
                and all(_finite(y) for y in x) and x[0] <= x[1])
    if isinstance(v, dict):
        return len(v) > 0 and all(_text(k) and one(x) for k, x in v.items())
    return one(v)


FIELD_CHECKS = {"task_id": _text, "sender": _text, "recipient": _text,
                "action_proposal": _text, "assumptions": _text_or_list,
                "uncertainty": _uncertainty_ok,
                "authorization_scope": _text_or_list,
                "safety_status": lambda v: v in SAFETY_STATUSES}


def envelope_gate(proposal):
    """Gate rule for a safety-aware message envelope (Algorithm 7.1).

    A field counts as present only if it has the required type and
    content: empty strings, lists or dicts, non-finite numbers and
    statuses other than green/yellow/red are treated as missing.
    red safety status -> refuse; uncertainty, authorization scope or
    safety status missing or invalid -> escalate (the collective check
    cannot be run); any other missing field -> reformulate;
    complete -> proceed.  Returns (missing or invalid fields, outcome).
    """
    if not isinstance(proposal, dict):
        return list(ENVELOPE_FIELDS), LADDER[2]
    missing = [f for f in ENVELOPE_FIELDS
               if not FIELD_CHECKS[f](proposal.get(f))]
    if proposal.get("safety_status") == "red":
        return missing, LADDER[3]
    if not missing:
        return missing, "proceed"
    if any(f in missing for f in GATE_CRITICAL):
        return missing, LADDER[2]
    return missing, LADDER[0]


def ch07_negotiation_gate():
    """The worked case: seven of eight fields, uncertainty missing."""
    proposal = {"task_id": "T-908", "sender": "agent-B", "recipient": "agent-C",
                "action_proposal": "confirm dispatch", "assumptions": "lane free",
                "uncertainty": None, "authorization_scope": "write:schedule",
                "safety_status": "green"}
    missing, outcome = envelope_gate(proposal)
    return len(ENVELOPE_FIELDS), len(ENVELOPE_FIELDS) - len(missing), missing, outcome


# ---------------------------------------------------------------- ch08
def ch08_aging_scheduler(base=(2.0, 1.0, 1.4), aging=0.25, horizon=12):
    """Anti-starvation by aging.

    Three always-backlogged classes (0 urgent, 1 routine, 2 vulnerable-
    complex) share one service per hour.  Priority = base weight + aging
    increment per hour since the class was last served; ties go to the
    more urgent class.  Returns (services per class, longest wait per
    class including a wait still open at the end of the day).
    """
    served, longest, since = [0, 0, 0], [0, 0, 0], [0, 0, 0]
    for _ in range(horizon):
        prio = [base[c] + aging * since[c] for c in range(3)]
        top = max(range(3), key=lambda c: (prio[c], -c))
        served[top] += 1
        longest[top] = max(longest[top], since[top])
        since = [0 if c == top else since[c] + 1 for c in range(3)]
    longest = [max(longest[c], since[c]) for c in range(3)]
    return served, longest


def ch08_no_aging_sink(base=(2.0, 1.0, 1.4), horizon=12):
    """Counterfactual with aging disabled: the lower classes starve."""
    return ch08_aging_scheduler(base=base, aging=0.0, horizon=horizon)


def ch08_aging_with_deadline(base=(2.0, 1.0, 1.4), aging=0.25, horizon=12,
                             max_wait=(None, None, 3)):
    """Aging plus a guaranteed-service deadline: a class whose wait has
    reached its deadline is served next, whatever the priorities say
    (the vulnerable-complex class here gets a 3-hour deadline)."""
    served, longest, since = [0, 0, 0], [0, 0, 0], [0, 0, 0]
    for _ in range(horizon):
        due = [c for c in range(3) if max_wait[c] is not None and since[c] >= max_wait[c]]
        if due:
            top = max(due, key=lambda c: (since[c], -c))
        else:
            prio = [base[c] + aging * since[c] for c in range(3)]
            top = max(range(3), key=lambda c: (prio[c], -c))
        served[top] += 1
        longest[top] = max(longest[top], since[top])
        since = [0 if c == top else since[c] + 1 for c in range(3)]
    longest = [max(longest[c], since[c]) for c in range(3)]
    return served, longest


# ---------------------------------------------------------------- ch09
LEDGER_EVENTS = ["E1: propose x1y2", "E2: collective check 0.55 > XI 0.40",
                 "E3: block x1y2", "E4: reformulate x1y1",
                 "E5: collective check 0.30 <= XI 0.40"]
GENESIS = "0" * 64          # full-length genesis value


def _link(prev, ev):
    """Full 256-bit SHA-256 link (64 hex digits); never truncated."""
    return hashlib.sha256((prev + ev).encode("utf-8")).hexdigest()


def short(h, n=8):
    """Display form of a hash, for printing only; store the full hash."""
    return h[:n] + "..."


def ledger_build(events):
    chain, prev = [], GENESIS
    for ev in events:
        h = _link(prev, ev)
        chain.append((ev, h))
        prev = h
    return chain


def ledger_verify(chain):
    """Recompute the chain from genesis; a link is valid only if its stored
    hash equals the recomputed one.  Returns (valid count, first bad index
    (1-based) or None).

    A chain that is internally consistent is not proof of an unchanged
    history: someone who rewrites every later record and hash, or
    deletes the final records, leaves a chain that verifies.  Detecting
    that needs a trusted external checkpoint (ledger_verify_anchor)."""
    prev, ok = GENESIS, []
    for ev, stored in chain:
        h = _link(prev, ev)
        ok.append(h == stored)
        prev = h
    first_bad = next((i + 1 for i, v in enumerate(ok) if not v), None)
    valid = ok.index(False) if False in ok else len(ok)
    return valid, first_bad


def ledger_verify_anchor(chain, anchor_len, anchor_hash):
    """Check a chain against an externally published checkpoint
    (Section 9.9): the record count and full head hash published at
    that time.  Returns True only if the chain still contains that head
    at that position and verifies up to it."""
    if len(chain) < anchor_len or anchor_len < 1:
        return False                      # records deleted
    valid, _ = ledger_verify(chain[:anchor_len])
    return valid == anchor_len and chain[anchor_len - 1][1] == anchor_hash


def ch09_ledger_hash():
    """Honest chain versus a chain whose third record was edited."""
    chain = ledger_build(LEDGER_EVENTS)
    honest = ledger_verify(chain)
    tampered = list(chain)
    tampered[2] = ("E3: approve x1y2", chain[2][1])   # content edited, hash kept
    return len(chain), honest, ledger_verify(tampered)


# ---------------------------------------------------------------- ch10
def ch10_patient_priority(freshness_bound=0.50):
    """Two agents propose different patients for one imaging slot.

    Priority Z = 0.5*acuity + 0.25*pain + 0.25*vulnerability (PRPA-style
    pain signal as support, not verdict).  Record staleness is a separate
    gate: a proposal built on a record staler than the bound is returned
    for refresh instead of being ranked.
    Returns (Z1, Z2, proposals that pass the gate, slot assignment).
    """
    p = {"P1": dict(acuity=0.90, pain=0.70, vuln=0.80, stale=0.10),
         "P2": dict(acuity=0.75, pain=0.50, vuln=0.40, stale=0.60)}

    def z(r):
        return round(0.50 * r["acuity"] + 0.25 * r["pain"] + 0.25 * r["vuln"], 3)

    passing = [k for k, r in p.items() if r["stale"] <= freshness_bound]
    winner = max(passing, key=lambda k: z(p[k])) if passing else None
    return z(p["P1"]), z(p["P2"]), passing, winner


# ---------------------------------------------------------------- ch11
def ch11_drone_corridor(v=8.0, tau_sep=4.0, s0=10.0, length=1200.0,
                        density_per_km=6.0):
    """Longitudinal spacing v*tau + s0, slot capacity and occupancy."""
    gap = v * tau_sep + s0
    slots = int(length // gap)
    occupancy = round(density_per_km * (length / 1000.0), 1)
    return round(gap, 1), slots, occupancy


def ch11_ground_exposure(bystanders=25, coeff=0.40, margin=0.35, limit=12.0):
    """Ground-exposure envelope: exposure plus safety margin must stay
    within the policy limit.  Returns (exposure, margin, required, ok)."""
    base = round(bystanders * coeff, 2)
    margin_value = round(base * margin, 2)
    required = round(base + margin_value, 2)
    return base, margin_value, required, required <= limit


# ---------------------------------------------------------------- ch12
def ch12_market_amplifier(n_agents=8, rho=0.25, individual=0.02,
                          systemic_limit=0.03):
    """Correlated strategies: aggregate move a*(1 + rho*(n-1))."""
    aggregate = individual * (1 + rho * (n_agents - 1))
    return round(aggregate, 4), systemic_limit, aggregate > systemic_limit


def ch12_flash_decay(alpha=0.35, theta=0.55, loops=3):
    """Circuit-breaker suppression recurrence x <- alpha * x**theta."""
    x = [1.00]
    for _ in range(loops):
        x.append(alpha * (x[-1] ** theta))
    return [round(v, 3) for v in x]


def aggregate_breaker(exposures, limit=0.03, rho=0.25):
    """Joint-action breaker: correlation-adjusted aggregate exposure of
    the strategies that fired together, checked outside every agent.

    A = max(e) + rho * (sum(e) - max(e)): the largest exposure counts in
    full and every other correlated strategy adds the fraction rho of
    its own.  For n equal exposures a this equals a*(1 + rho*(n-1)).
    Adding a strategy can never lower A, so small orders cannot dilute
    a large one below the limit.  Exposures are magnitudes (>= 0) in the
    aligned direction.  Invalid inputs fail closed (halt-new-orders).
    Returns (aggregate or None, action)."""
    try:
        e = list(exposures)
    except TypeError:
        return None, "halt-new-orders"
    if not (_finite(limit, 0.0) and _finite(rho, 0.0) and rho <= 1.0
            and all(_finite(x, 0.0) for x in e)):
        return None, "halt-new-orders"
    if not e:
        return 0.0, "allow"
    top = max(e)
    agg = round(top + rho * (sum(e) - top), 10)
    return round(agg, 4), ("halt-new-orders" if agg > limit else "allow")


# ---------------------------------------------------------------- ch13
def ch13_floor_sets():
    """Three jurisdictions: floors all three share versus floors a
    deployment must hold to satisfy all three at once."""
    A = {"consent", "audit", "oversight", "nondiscrimination", "escalation"}
    B = {"consent", "audit", "oversight", "safety-envelope"}
    C = {"consent", "nondiscrimination", "escalation", "safety-envelope"}
    common = A & B & C
    union = A | B | C
    return len(common), len(union), sorted(common), sorted(union - common)


# ---------------------------------------------------------------- ch14
def ch14_capability_constraint(cap_rate=1.35, ctr_rate=1.15, periods=8):
    """Capability versus verified constraint reach after n cycles."""
    cap, ctr = cap_rate ** periods, ctr_rate ** periods
    return round(cap, 2), round(ctr, 2), round(cap / ctr, 2)


def ch14_overrun_budget(periods=8, cap_rate=1.35, ctr_rate=1.15,
                        base_margin=1.0):
    """Safety margin per unit of capability when constraint growth lags."""
    return round(base_margin * ((ctr_rate / cap_rate) ** periods), 3)


def ch14_required_constraint_rate(cap_rate=1.35, periods=8, min_margin=0.80):
    """Constraint growth rate needed per cycle to keep the margin at or
    above min_margin after `periods` cycles of capability growth."""
    return round(cap_rate * min_margin ** (1.0 / periods), 4)


# ---------------------------------------------------------------- ch15
MATURITY_LEVELS = ["informal principles", "documented policies and ownership",
                   "enforced permissions and safety checks",
                   "system-level testing, monitoring and incident response",
                   "continuous independent evaluation"]


def ch15_maturity(counts=(3, 3, 2, 1, 0), needed=2):
    """A level counts only if it and every level below it have at least
    `needed` working controls.  Returns (level reached, first gap level)."""
    level = 0
    for c in counts:
        if c >= needed:
            level += 1
        else:
            break
    gap = level + 1 if level < len(counts) else None
    return level, gap


def ch15_deployment_refusal(severe_modes=3, mitigated=2, contestation=True):
    """Refusal screen: every severe collective-harm mode must be mitigated
    and affected people must have a contestation route."""
    unmitigated = severe_modes - mitigated
    if unmitigated > 0:
        return unmitigated, "refuse"
    if not contestation:
        return 0, "refuse"
    return 0, "proceed"


if __name__ == "__main__":
    rows = [
        ("ch01_emergent_risk", ch01_emergent_risk()),
        ("ch01_pearson_joint", ch01_pearson_joint()),
        ("ch01_chain_handoff", ch01_chain_handoff()),
        ("ch01_harm_screen", ch01_harm_screen()),
        ("ch02_least_harm_option", ch02_least_harm_option()[1:]),
        ("ch03_floor_coverage", ch03_floor_coverage(FLOOR_E, FLOOR_C)),
        ("ch04_joint_feasibility", ch04_joint_feasibility()),
        ("ch05_floor_game", ch05_floor_game()),
        ("ch06_trajectory_harm", ch06_trajectory_harm()),
        ("ch06_early_escalation", ch06_early_escalation()),
        ("ch07_negotiation_gate", ch07_negotiation_gate()),
        ("ch08_aging_scheduler", ch08_aging_scheduler()),
        ("ch08_no_aging_sink", ch08_no_aging_sink()),
        ("ch08_aging_with_deadline", ch08_aging_with_deadline()),
        ("ch09_ledger_hash", ch09_ledger_hash()),
        ("ch10_patient_priority", ch10_patient_priority()),
        ("ch11_drone_corridor", ch11_drone_corridor()),
        ("ch11_ground_exposure", ch11_ground_exposure()),
        ("ch11_reroute", ch11_ground_exposure(bystanders=15)),
        ("ch12_market_amplifier", ch12_market_amplifier()),
        ("ch12_flash_decay", ch12_flash_decay()),
        ("ch12_aggregate_breaker", aggregate_breaker([0.02] * 8)),
        ("ch12_breaker_three", aggregate_breaker([0.02] * 3)),
        ("ch12_breaker_single", aggregate_breaker([0.04])),
        ("ch12_breaker_diluted", aggregate_breaker([0.04, 0.0001])),
        ("ch13_floor_sets", ch13_floor_sets()),
        ("ch14_capability_constraint", ch14_capability_constraint()),
        ("ch14_cycle4", ch14_capability_constraint(periods=4)),
        ("ch14_overrun_budget", ch14_overrun_budget()),
        ("ch14_required_rate", ch14_required_constraint_rate()),
        ("ch15_maturity", ch15_maturity()),
        ("ch15_deployment_refusal", ch15_deployment_refusal()),
    ]
    for name, value in rows:
        print(f"{name:27s} {value}")
