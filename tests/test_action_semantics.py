import unittest

from press_based_skin_fold_retraction.action_semantics import (
    ControlPhase,
    decode_action,
    project_action,
)


class ProjectActionTest(unittest.TestCase):
    def setUp(self):
        self.action = (0.4, -0.5, 0.6, 0.1, -0.2, 0.3, 0.9)

    def test_free_space_uses_pose_dimensions(self):
        self.assertEqual(
            project_action(self.action, ControlPhase.FREE_SPACE),
            (0.4, -0.5, 0.6, 0.1, -0.2, 0.3, 0.0),
        )

    def test_precontact_uses_only_approach_translation(self):
        self.assertEqual(
            project_action(self.action, ControlPhase.PRECONTACT_Z_ONLY),
            (0.0, 0.0, 0.6, 0.0, 0.0, 0.0, 0.0),
        )

    def test_contact_uses_tangential_position_and_normal_force(self):
        self.assertEqual(
            project_action(self.action, ControlPhase.CONTACT_HYBRID),
            (0.4, -0.5, 0.0, 0.0, 0.0, 0.0, 0.9),
        )

    def test_phase_name_is_case_insensitive(self):
        self.assertEqual(
            project_action(self.action, "contact_hybrid"),
            project_action(self.action, ControlPhase.CONTACT_HYBRID),
        )

    def test_normalized_values_are_clipped(self):
        action = (2.0, -3.0, 0.0, 0.0, 0.0, 0.0, 4.0)
        self.assertEqual(
            project_action(action, ControlPhase.CONTACT_HYBRID),
            (1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0),
        )

    def test_invalid_action_is_rejected(self):
        with self.assertRaises(ValueError):
            project_action((0.0,) * 6, ControlPhase.FREE_SPACE)
        with self.assertRaises(ValueError):
            project_action((0.0,) * 6 + (float("nan"),), ControlPhase.FREE_SPACE)


class DecodeActionTest(unittest.TestCase):
    def test_contact_scaling(self):
        command = decode_action(
            (0.5, -0.25, 0.8, 0.1, 0.2, 0.3, 0.4),
            ControlPhase.CONTACT_HYBRID,
            position_scale=0.02,
            rotation_scale=0.05,
            normal_force_scale=5.0,
        )

        self.assertEqual(command.position_delta, (0.01, -0.005, 0.0))
        self.assertEqual(command.rotation_delta, (0.0, 0.0, 0.0))
        self.assertEqual(command.normal_force_delta, 2.0)
        self.assertEqual(
            command.active_dimensions,
            ("delta_x", "delta_y", "delta_normal_force"),
        )

    def test_negative_scale_is_rejected(self):
        with self.assertRaises(ValueError):
            decode_action(
                (0.0,) * 7,
                ControlPhase.FREE_SPACE,
                position_scale=-0.01,
                rotation_scale=0.02,
                normal_force_scale=1.0,
            )


if __name__ == "__main__":
    unittest.main()
