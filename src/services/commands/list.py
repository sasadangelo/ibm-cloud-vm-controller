# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from typing import Any
from ibm_cloud_sdk_core.detailed_response import DetailedResponse
from core import LoggerManager
from dtos import VSI
from services.commands.base import BaseCommand, CommandResult
from services.commands.ibm_vpc_client import IBMVPCClient


class ListVSICommand(BaseCommand[list[VSI]]):
    def __init__(self, region: str) -> None:
        """
        Initialize with the IBM Cloud region.

        :param region: IBM Cloud region (e.g., "us-south", "us-east", "eu-de").
        """
        self.region = region
        self.log = LoggerManager.get_logger(self.__class__.__name__)
        self.vpc_client = IBMVPCClient(region=region).get_client()

    def execute(self) -> CommandResult[list[VSI]]:
        """
        List all VSIs in the specified region.

        :return: CommandResult with list of VSI DTOs on success,
                 or error message on failure.
        """
        self.log.debug(f"Calling IBM VPC API list_instances for region='{self.region}'")
        # Make a request to the IBM Cloud VPC API to list all instances
        response: DetailedResponse = self.vpc_client.list_instances()
        status = response.get_status_code()
        # Check if the API call was successful
        if status != 200:
            self.log.error(f"list_instances returned HTTP {status}: {response.get_result()}")
            return CommandResult(
                success=False,
                message=f"Error listing VMs: {response.get_result()}",
                data=None,
            )
        # Extract the list of instance dictionaries from the response
        result: dict[str, Any] = response.get_result()  # type: ignore[assignment]
        instances: list[dict[str, Any]] = result.get("instances", [])
        self.log.debug(f"API returned {len(instances)} instance(s)")
        # Convert each instance dictionary into a VSI DTO, mapping API fields to model fields
        vsi_list: list[VSI] = [
            VSI(
                id=data["id"],
                name=data["name"],
                status=data["status"],
                zone=data["zone"]["name"],
                cpu=data["vcpu"]["count"],
                ram=data["memory"] * 1024,
            )
            for data in instances
        ]
        for vsi in vsi_list:
            self.log.debug(f"  → VSI: id='{vsi.id}' name='{vsi.name}' status='{vsi.status}' zone='{vsi.zone}'")
        return CommandResult(
            success=True,
            message="VM list retrieved successfully.",
            data=vsi_list,
        )


# Made with Bob
