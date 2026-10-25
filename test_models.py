"""Checks that the companion program reproduces every number printed in
"No-Harm Principles in AI Architectures" (First Edition, 2026).
Run:  python -m unittest test_models.py
"""
import unittest

import models_no_harm_principles_in_ai_architectures as m


class TestBookNumbers(unittest.TestCase):
    def test_ch01(self):
        self.assertEqual(m.ch01_emergent_risk(), (0.0016, 0.0088, 4.05, 0.0444))
        self.assertEqual(m.ch01_chain_handoff(), (0.8853, 0.1147))
        self.assertEqual(m.ch01_harm_screen(), 0.1584)

    def test_ch02(self):
        scored, admissible, chosen, util = m.ch02_least_harm_option()
        self.assertEqual([scored[k]["pi"] for k in "ABCD"], [3.6, 1.4, 1.2, 0.2])
        self.assertEqual((admissible, chosen, util), (["B", "C", "D"], "D", "B"))

    def test_ch03(self):
        self.assertEqual(m.ch03_floor_coverage(m.FLOOR_E, m.FLOOR_C), (5, 8, 0.625, [1, 4, 6]))

    def test_ch04(self):
        self.assertEqual(m.ch04_joint_feasibility(),
                         (6, 4, [(1, 2), (2, 2)], (1, 2), 1.7, (1, 1), 1.5))

    def test_ch04_filter(self):
        ux, uy = (0.90, 0.75, 0.40), (0.60, 0.80, 0.50)
        props = [(x, y) for x in (1, 2, 3) for y in (1, 2, 3)]
        chosen, a_cf, rej = m.collective_filter(
            props, lambda a: a[0] != 3, lambda a: m.INTERACTION.get(a, 1.0), 0.40,
            lambda a: ux[a[0] - 1] + uy[a[1] - 1])
        self.assertEqual(chosen, (1, 1))
        self.assertEqual(len(a_cf), 4)
        self.assertEqual(sum(1 for _, r in rej if r == "individual"), 3)

    def test_ch05(self):
        g0, g1, g2 = m.ch05_floor_game()
        self.assertEqual(g0, ([("D", "D")], (1.0, 1.0)))
        self.assertEqual(g1, ([("C", "C")], (3.0, 3.0)))
        self.assertEqual(g2, ([("Dm", "Dm")], (2.2, 2.2)))

    def test_ch06(self):
        self.assertEqual(m.ch06_trajectory_harm(), (0.272, 0.395, 0.3641))
        self.assertEqual(m.ch06_early_escalation(), ([0.04, 0.11, 0.21, 0.34], 3, 6))

    def test_ch07(self):
        self.assertEqual(m.ch07_negotiation_gate(), (8, 7, ["uncertainty"], "escalate"))
        ok = {f: "x" for f in m.ENVELOPE_FIELDS}
        self.assertEqual(m.envelope_gate(ok)[1], "proceed")
        self.assertEqual(m.envelope_gate(dict(ok, assumptions=None))[1], "reformulate")
        self.assertEqual(m.envelope_gate(dict(ok, safety_status="red"))[1], "refuse")

    def test_ch08(self):
        self.assertEqual(m.ch08_aging_scheduler(), ([8, 2, 2], [1, 5, 4]))
        self.assertEqual(m.ch08_no_aging_sink(), ([12, 0, 0], [0, 12, 12]))
        self.assertEqual(m.ch08_aging_with_deadline(), ([8, 1, 3], [1, 6, 3]))

    def test_ch09(self):
        self.assertEqual(m.ch09_ledger_hash(), (5, (5, None), (2, 3)))

    def test_ch10(self):
        self.assertEqual(m.ch10_patient_priority(), (0.825, 0.6, ["P1"], "P1"))

    def test_ch11(self):
        self.assertEqual(m.ch11_drone_corridor(), (42.0, 28, 7.2))
        self.assertEqual(m.ch11_ground_exposure(), (10.0, 3.5, 13.5, False))
        self.assertEqual(m.ch11_ground_exposure(bystanders=15), (6.0, 2.1, 8.1, True))

    def test_ch12(self):
        self.assertEqual(m.ch12_market_amplifier(), (0.055, 0.03, True))
        self.assertEqual(m.ch12_flash_decay(), [1.0, 0.35, 0.196, 0.143])
        self.assertEqual(m.aggregate_breaker([0.02] * 8), (0.055, "halt-new-orders"))
        self.assertEqual(m.aggregate_breaker([0.02] * 3), (0.03, "allow"))

    def test_ch13(self):
        n_common, n_union, common, rest = m.ch13_floor_sets()
        self.assertEqual((n_common, n_union, common), (1, 6, ["consent"]))
        self.assertEqual(len(rest), 5)

    def test_ch14(self):
        self.assertEqual(m.ch14_capability_constraint(), (11.03, 3.06, 3.61))
        self.assertEqual(m.ch14_capability_constraint(periods=4), (3.32, 1.75, 1.9))
        self.assertEqual(m.ch14_overrun_budget(), 0.277)
        self.assertEqual(m.ch14_required_constraint_rate(), 1.3129)

    def test_ch15(self):
        self.assertEqual(m.ch15_maturity(), (3, 4))
        self.assertEqual(m.ch15_deployment_refusal(), (1, "refuse"))
        self.assertEqual(m.ch15_deployment_refusal(mitigated=3), (0, "proceed"))
        self.assertEqual(m.ch15_deployment_refusal(mitigated=3, contestation=False), (0, "refuse"))


if __name__ == "__main__":
    unittest.main()
