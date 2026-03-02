# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
import unittest
from dtos import VSI
from services import CommandResult, VSIController


class TestVSIController(unittest.TestCase):
    def setUp(self) -> None:
        # Instantiate the controller once for all tests
        self.controller = VSIController(region="us-east")

    def test_list_vsi(self) -> None:
        """Test listing VSI instances (requires at least one VSI to exist)."""
        result: CommandResult[list[VSI]] = self.controller.list_vsi()
        self.assertTrue(expr=result.success, msg=f"List failed: {result.message}")
        self.assertIsInstance(obj=result.data, cls=list)
        assert result.data is not None
        self.assertGreater(len(result.data), 0, "Expected at least one VSI in the list.")

    def test_stop_start_vsi(self) -> None:
        """Test stopping and starting a VSI by ID (assumes a 'test-vm' exists)."""
        list_result: CommandResult[list[VSI]] = self.controller.list_vsi()
        self.assertTrue(expr=list_result.success, msg=f"List failed: {list_result.message}")
        self.assertIsNotNone(obj=list_result.data)
        assert list_result.data is not None

        # Find VSI by name
        vsi: VSI | None = next((v for v in list_result.data if v.name == "matteo-test"), None)
        self.assertIsNotNone(obj=vsi, msg="VSI named 'matteo-test' not found.")
        assert vsi is not None

        # Stop VSI
        stop_result: CommandResult[str | None] = self.controller.stop_vsi(vsi_id=vsi.id)
        self.assertTrue(expr=stop_result.success, msg=f"Stop failed: {stop_result.message}")

        # Start VSI
        start_result: CommandResult[str | None] = self.controller.start_vsi(vsi_id=vsi.id)
        self.assertTrue(expr=start_result.success, msg=f"Start failed: {start_result.message}")

    def test_stop_invalid_vsi(self) -> None:
        """Test stopping a VSI with an invalid ID to trigger error handling."""
        invalid_id = "fake-vsi-id"
        result: CommandResult[str | None] = self.controller.stop_vsi(vsi_id=invalid_id)
        self.assertFalse(expr=result.success)
        self.assertIn(member="Failed", container=result.message)


if __name__ == "__main__":
    unittest.main()
