# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from ibm_cloud_sdk_core.detailed_response import DetailedResponse
from core import LoggerManager
from services.commands.base import BaseCommand, CommandResult
from services.commands.ibm_vpc_client import IBMVPCClient


class StopVSICommand(BaseCommand[str | None]):
    def __init__(self, region: str, vsi_id: str) -> None:
        """
        :param region: IBM Cloud region (e.g., "us-south", "us-east", "eu-de").
        :param vsi_id: ID of the VSI to stop.
        """
        self.vsi_id = vsi_id
        self.log = LoggerManager.get_logger(self.__class__.__name__)
        self.vpc_client = IBMVPCClient(region=region).get_client()

    def execute(self) -> CommandResult[str | None]:
        """
        Stop the VSI identified by vsi_id in the specified region.

        Returns:
            CommandResult containing success status and optional message.
        """
        self.log.debug(f"Calling IBM VPC API create_instance_action(stop) for VSI id='{self.vsi_id}'")
        try:
            resp: DetailedResponse = self.vpc_client.create_instance_action(instance_id=self.vsi_id, type="stop")
        except Exception as e:
            self.log.error(f"Exception while stopping VSI id='{self.vsi_id}': {e}")
            return CommandResult(success=False, message=f"Failed to stop VSI: {e}")
        status = resp.get_status_code()
        if status == 201:
            self.log.info(f"VSI id='{self.vsi_id}' stop action accepted (HTTP {status})")
            return CommandResult(success=True, message=f"VSI '{self.vsi_id}' stopped successfully.")
        else:
            self.log.warning(f"VSI id='{self.vsi_id}' stop action rejected (HTTP {status}): {resp.get_result()}")
            return CommandResult(success=False, message=f"Failed to stop VSI: {resp.get_result()}")


# Made with Bob
