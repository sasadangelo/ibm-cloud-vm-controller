# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from typing import Any
from ibm_cloud_sdk_core.detailed_response import DetailedResponse
from dtos import VSI
from services.commands.base import BaseCommand, CommandResult
from services.commands.ibm_vpc_client import IBMVPCClient


class ListVSICommand(BaseCommand[list[VSI]]):
    def __init__(self) -> None:
        """
        Initialize with the IBM Cloud zone (availability zone).

        :param zone: IBM Cloud zone (e.g., "us-south-1").
        """
        # Instantiate the VPC client for the given zone
        self.vpc_client = IBMVPCClient().get_client()

    def execute(self) -> CommandResult[list[VSI]]:
        """
        List VSIs in the specified zone.

        :return: CommandResult with list of VSI DTOs on success,
                 or error message on failure.
        """
        # Make a request to the IBM Cloud VPC API to list all instances
        response: DetailedResponse = self.vpc_client.list_instances()
        # Check if the API call was successful
        if response.get_status_code() != 200:
            # Return a failure result with the error message
            return CommandResult(
                success=False,
                message=f"Error listing VMs: {response.get_result()}",
                data=None,
            )
        # Extract the list of instance dictionaries from the response
        result: dict[str, Any] = response.get_result()  # type: ignore[assignment]
        instances: list[dict[str, Any]] = result.get("instances", [])
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
        # Return a successful CommandResult containing the list of VSI objects
        return CommandResult(
            success=True,
            message="VM list retrieved successfully.",
            data=vsi_list,
        )
