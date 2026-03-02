# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from core import LoggerManager
from dtos import VSI
from services.commands import CommandResult, ListVSICommand, StartVSICommand, StopVSICommand


class VSIController:
    """
    High-level interface for controlling IBM Cloud Virtual Server Instances.
    """

    def __init__(self, region: str = "us-south") -> None:
        self.region = region
        self.log = LoggerManager.get_logger(self.__class__.__name__)
        self.log.debug(f"VSIController initialized for region='{region}'")

    def list_vsi(self) -> CommandResult[list[VSI]]:
        """
        List all VSIs in the configured region.

        :return: CommandResult with list of VSI DTOs
        """
        self.log.info(f"Listing VSIs in region='{self.region}'")
        result = ListVSICommand(region=self.region).execute()
        if result.success:
            count = len(result.data) if result.data else 0
            self.log.info(f"Found {count} VSI(s) in region='{self.region}'")
        else:
            self.log.warning(f"Failed to list VSIs in region='{self.region}': {result.message}")
        return result

    def start_vsi(self, vsi_id: str) -> CommandResult[str | None]:
        """
        Start a VSI by its ID.

        :param vsi_id: ID of the VSI to start
        :return: CommandResult with optional success message
        """
        self.log.info(f"Requesting start for VSI id='{vsi_id}' in region='{self.region}'")
        result = StartVSICommand(region=self.region, vsi_id=vsi_id).execute()
        if result.success:
            self.log.info(f"VSI id='{vsi_id}' start request accepted: {result.message}")
        else:
            self.log.warning(f"VSI id='{vsi_id}' start request failed: {result.message}")
        return result

    def stop_vsi(self, vsi_id: str) -> CommandResult[str | None]:
        """
        Stop a VSI by its ID.

        :param vsi_id: ID of the VSI to stop
        :return: CommandResult with optional success message
        """
        self.log.info(f"Requesting stop for VSI id='{vsi_id}' in region='{self.region}'")
        result = StopVSICommand(region=self.region, vsi_id=vsi_id).execute()
        if result.success:
            self.log.info(f"VSI id='{vsi_id}' stop request accepted: {result.message}")
        else:
            self.log.warning(f"VSI id='{vsi_id}' stop request failed: {result.message}")
        return result


# Made with Bob
