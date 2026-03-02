# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from ibm_cloud_sdk_core.detailed_response import DetailedResponse
from services.commands.base import BaseCommand, CommandResult
from services.commands.ibm_vpc_client import IBMVPCClient


class StopVSICommand(BaseCommand[str | None]):
    def __init__(self, vsi_id: str) -> None:
        self.vsi_id = vsi_id
        # Instantiate the VPC client for the given zone
        self.vpc_client = IBMVPCClient().get_client()

    def execute(self) -> CommandResult[str | None]:
        """
        Stops the VSI with the given ID in the specified region.

        Returns:
            CommandResult containing success status and optional message.
        """
        # Directly attempt to stop the VSI by ID
        try:
            # Attempt to send the stop action to the VSI instance
            resp: DetailedResponse = self.vpc_client.create_instance_action(instance_id=self.vsi_id, type="stop")
        except Exception as e:
            # Return a failure result with the exception message
            return CommandResult(success=False, message=f"Failed to stop VSI: {e}")
        # If the API call returns HTTP 201, the stop action succeeded
        if resp.get_status_code() == 201:
            return CommandResult(success=True, message=f"VSI '{self.vsi_id}' stopped successfully.")
        else:
            # Extract and return the error details from the response
            return CommandResult(success=False, message=f"Failed to stop VSI: {resp.get_result()}")
