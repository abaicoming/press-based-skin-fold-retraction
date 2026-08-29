import unittest

from press_based_skin_fold_retraction.action_semantics import (
    ContactState,
    interpret_action,
)


class InterpretActionTest(unittest.TestCase):
    def setUp(self):
        self.action = (0.4, -0.5, 0.6, 0.1, -0.2, 0.3, 12.0)

    def test_non_contact_executes_pose_and_ignores_force_target(self):
        interpreted = interpret_action(self.action, ContactState.NON_CONTACT)

        self.assertEqual(interpreted.position_increment, (0.4, -0.5, 0.6))
        self.assertEqual(interpreted.orientation_increment, (0.1, -0.2, 0.3))
        self.assertIsNone(interpreted.desired_normal_force)

    def test_contact_discards_normal_position_and_orientation(self):
        interpreted = interpret_action(
            self.action,
            ContactState.CONTACT,
            tool_normal=(0.0, 0.0, 1.0),
        )

        self.assertEqual(interpreted.position_increment, (0.4, -0.5, 0.0))
        self.assertEqual(interpreted.orientation_increment, (0.0, 0.0, 0.0))
        self.assertEqual(interpreted.desired_normal_force, 12.0)

    def test_contact_projection_uses_the_supplied_tool_normal(self):
        interpreted = interpret_action(
            (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.0),
            ContactState.CONTACT,
            tool_normal=(1.0, 1.0, 0.0),
        )

        self.assertAlmostEqual(interpreted.position_increment[0], 0.5)
        self.assertAlmostEqual(interpreted.position_increment[1], -0.5)
        self.assertAlmostEqual(interpreted.position_increment[2], 0.0)

    def test_tool_normal_is_normalized(self):
        unit = interpret_action(
            self.action,
            ContactState.CONTACT,
            tool_normal=(0.0, 0.0, 1.0),
        )
        scaled = interpret_action(
            self.action,
            ContactState.CONTACT,
            tool_normal=(0.0, 0.0, 5.0),
        )
        self.assertEqual(unit, scaled)

    def test_contact_requires_a_valid_tool_normal(self):
        with self.assertRaises(ValueError):
            interpret_action(self.action, ContactState.CONTACT)
        with self.assertRaises(ValueError):
            interpret_action(
                self.action,
                ContactState.CONTACT,
                tool_normal=(0.0, 0.0, 0.0),
            )

    def test_invalid_action_or_state_is_rejected(self):
        with self.assertRaises(ValueError):
            interpret_action((0.0,) * 6, ContactState.NON_CONTACT)
        with self.assertRaises(ValueError):
            interpret_action(
                (0.0,) * 6 + (float("nan"),),
                ContactState.NON_CONTACT,
            )
        with self.assertRaises(ValueError):
            interpret_action(self.action, 2)


if __name__ == "__main__":
    unittest.main()
