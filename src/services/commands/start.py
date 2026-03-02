# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from ibm_cloud_sdk_core.detailed_response import DetailedResponse
from services.commands.base import BaseCommand, CommandResult
from services.commands.ibm_vpc_client import IBMVPCClient


class StartVSICommand(BaseCommand[str | None]):
    def __init__(self, vsi_id: str) -> None:
        self.vsi_id = vsi_id
        self.vpc_client = IBMVPCClient().get_client()

    def execute(self) -> CommandResult[str | None]:
        """
        Start the VSI identified by vsi_id in the specified zone.

        Returns:
            CommandResult with success status and optional message.
        """
        # Directly attempt to start the VSI by ID
        try:
            # Attempt to send the start action to the VSI instance
            resp: DetailedResponse = self.vpc_client.create_instance_action(instance_id=self.vsi_id, type="start")
        except Exception as e:
            # Return a failure result with the exception message
            return CommandResult(success=False, message=f"Exception occurred while starting VSI: {e}")
        # If the API call returns HTTP 201, the start action succeeded
        if resp.get_status_code() == 201:
            return CommandResult(success=True, message=f"VSI '{self.vsi_id}' started successfully.")
        else:
            # Extract and return the error details from the response
            return CommandResult(success=False, message=f"Failed to start VSI: {resp.get_result()}")
