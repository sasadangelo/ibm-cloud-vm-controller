# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from ibm_cloud_sdk_core.detailed_response import DetailedResponse
from core import LoggerManager
from services.commands.base import BaseCommand, CommandResult
from services.commands.ibm_vpc_client import IBMVPCClient


class DeleteVSICommand(BaseCommand[str | None]):
    def __init__(self, region: str, vsi_id: str) -> None:
        """
        :param region: IBM Cloud region (e.g., "us-south", "us-east", "eu-de").
        :param vsi_id: ID of the VSI to delete.
        """
        self.vsi_id = vsi_id
        self.log = LoggerManager.get_logger(self.__class__.__name__)
        self.vpc_client = IBMVPCClient(region=region).get_client()

    def execute(self) -> CommandResult[str | None]:
        """
        Delete the VSI identified by vsi_id.

        The IBM VPC API returns HTTP 204 (No Content) on successful deletion.
        The VSI must be stopped before it can be deleted; if it is still running
        the API will return an error.

        Returns:
            CommandResult with success status and optional message.
        """
        self.log.debug(f"Calling IBM VPC API delete_instance for VSI id='{self.vsi_id}'")
        try:
            resp: DetailedResponse = self.vpc_client.delete_instance(id=self.vsi_id)
        except Exception as e:
            self.log.error(f"Exception while deleting VSI id='{self.vsi_id}': {e}")
            return CommandResult(success=False, message=f"Exception occurred while deleting VSI: {e}")

        status = resp.get_status_code()
        if status == 204:
            self.log.info(f"VSI id='{self.vsi_id}' deleted successfully (HTTP {status})")
            return CommandResult(success=True, message=f"VSI '{self.vsi_id}' deleted successfully.")
        else:
            self.log.warning(f"VSI id='{self.vsi_id}' delete rejected (HTTP {status}): {resp.get_result()}")
            return CommandResult(success=False, message=f"Failed to delete VSI: {resp.get_result()}")


# Made with Bob
