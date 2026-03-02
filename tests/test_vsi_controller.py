# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
import os
import unittest
from dotenv import load_dotenv
from dtos import VSI, VSITemplate
from services import CommandResult, VSIController

# Load environment variables from .env (if present)
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration — read from .env or fall back to empty strings
# ---------------------------------------------------------------------------
_REGION: str = os.environ.get("IBM_REGION", "us-east")
_VPC_ID: str = os.environ.get("VPC_ID", "")
_SUBNET_ID: str = os.environ.get("SUBNET_ID", "")
_IMAGE_ID: str = os.environ.get("IMAGE_ID", "")
_SSH_KEY_ID: str = os.environ.get("SSH_KEY_ID", "")
_PROFILE: str = os.environ.get("VSI_PROFILE", "bx2-2x8")
_VM_NAME = "test-vm"

# Skip integration tests if the required IBM Cloud IDs are not configured
_SKIP_INTEGRATION = not (_VPC_ID and _SUBNET_ID and _IMAGE_ID)
_SKIP_REASON = "VPC_ID, SUBNET_ID and IMAGE_ID must be set in .env to run integration tests"


@unittest.skipIf(_SKIP_INTEGRATION, _SKIP_REASON)
class TestVSIControllerIntegration(unittest.TestCase):
    """
    Integration test suite for VSIController.

    Lifecycle managed by setUpClass / tearDownClass:
      - setUpClass  → creates 'test-vm' once before all tests
      - tearDownClass → stops and deletes 'test-vm' once after all tests

    Individual tests operate on the shared VSI created in setUpClass,
    so no VSI needs to exist beforehand in the IBM Cloud account.
    """

    controller: VSIController
    vsi: VSI

    @classmethod
    def setUpClass(cls) -> None:
        """Create the test VSI once before all tests in this class."""
        cls.controller = VSIController(region=_REGION)
        template = VSITemplate(
            name=_VM_NAME,
            zone=f"{_REGION}-2",
            vpc_id=_VPC_ID,
            subnet_id=_SUBNET_ID,
            image_id=_IMAGE_ID,
            profile=_PROFILE,
            ssh_key_ids=[_SSH_KEY_ID] if _SSH_KEY_ID else [],
        )
        result: CommandResult[VSI] = cls.controller.create_vsi(template=template)
        if not result.success or not result.data:
            raise RuntimeError(f"setUpClass: failed to create test VSI — {result.message}")
        cls.vsi = result.data
        print(f"\n[setUpClass] VSI '{cls.vsi.name}' created with id='{cls.vsi.id}'")

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop and delete the test VSI once after all tests in this class."""
        # IBM Cloud requires the VSI to be stopped before deletion
        stop_result: CommandResult[str | None] = cls.controller.stop_vsi(vsi_id=cls.vsi.id)
        if not stop_result.success:
            print(f"\n[tearDownClass] Warning: stop failed — {stop_result.message}")

        delete_result: CommandResult[str | None] = cls.controller.delete_vsi(vsi_id=cls.vsi.id)
        if delete_result.success:
            print(f"\n[tearDownClass] VSI '{cls.vsi.name}' (id='{cls.vsi.id}') deleted.")
        else:
            print(f"\n[tearDownClass] Warning: delete failed — {delete_result.message}")

    def test_01_list_vsi_contains_test_vm(self) -> None:
        """After creation, 'test-vm' must appear in the VSI list."""
        result: CommandResult[list[VSI]] = self.controller.list_vsi()
        self.assertTrue(expr=result.success, msg=f"List failed: {result.message}")
        self.assertIsInstance(obj=result.data, cls=list)
        assert result.data is not None
        ids = [v.id for v in result.data]
        self.assertIn(
            member=self.vsi.id,
            container=ids,
            msg=f"VSI id='{self.vsi.id}' not found in list after creation.",
        )

    def test_02_stop_vsi(self) -> None:
        """Stop the test VSI and verify the operation succeeds."""
        result: CommandResult[str | None] = self.controller.stop_vsi(vsi_id=self.vsi.id)
        self.assertTrue(expr=result.success, msg=f"Stop failed: {result.message}")

    def test_03_start_vsi(self) -> None:
        """Start the test VSI and verify the operation succeeds."""
        result: CommandResult[str | None] = self.controller.start_vsi(vsi_id=self.vsi.id)
        self.assertTrue(expr=result.success, msg=f"Start failed: {result.message}")


class TestVSIControllerErrorHandling(unittest.TestCase):
    """
    Unit tests for VSIController error handling.

    These tests do not require a real IBM Cloud account or any .env configuration
    beyond API_KEY (which is needed to authenticate). They verify that invalid
    inputs are handled gracefully and return a failed CommandResult.
    """

    def setUp(self) -> None:
        self.controller = VSIController(region=_REGION)

    def test_stop_invalid_vsi(self) -> None:
        """Stopping a VSI with a fake ID must return a failure result."""
        result: CommandResult[str | None] = self.controller.stop_vsi(vsi_id="fake-vsi-id")
        self.assertFalse(expr=result.success)
        self.assertIn(member="Failed", container=result.message)

    def test_start_invalid_vsi(self) -> None:
        """Starting a VSI with a fake ID must return a failure result."""
        result: CommandResult[str | None] = self.controller.start_vsi(vsi_id="fake-vsi-id")
        self.assertFalse(expr=result.success)

    def test_delete_invalid_vsi(self) -> None:
        """Deleting a VSI with a fake ID must return a failure result."""
        result: CommandResult[str | None] = self.controller.delete_vsi(vsi_id="fake-vsi-id")
        self.assertFalse(expr=result.success)

    def test_create_invalid_vsi(self) -> None:
        """Creating a VSI with fake resource IDs must return a failure result."""
        template = VSITemplate(
            name="invalid-vm",
            zone="us-east-1",
            vpc_id="fake-vpc-id",
            subnet_id="fake-subnet-id",
            image_id="fake-image-id",
            profile="bx2-2x8",
        )
        result: CommandResult[VSI] = self.controller.create_vsi(template=template)
        self.assertFalse(expr=result.success, msg="Expected failure with invalid IDs.")


if __name__ == "__main__":
    unittest.main()

# Made with Bob
