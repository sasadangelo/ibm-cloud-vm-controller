# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from typing import Any
from ibm_cloud_sdk_core.detailed_response import DetailedResponse
from core import LoggerManager
from dtos import VSI, VSITemplate
from services.commands.base import BaseCommand, CommandResult
from services.commands.ibm_vpc_client import IBMVPCClient


class CreateVSICommand(BaseCommand[VSI]):
    def __init__(self, region: str, template: VSITemplate) -> None:
        """
        :param region: IBM Cloud region (e.g., "us-south", "us-east", "eu-de").
        :param template: VSITemplate with all parameters needed to create the VSI.
        """
        self.region = region
        self.template = template
        self.log = LoggerManager.get_logger(self.__class__.__name__)
        self.vpc_client = IBMVPCClient(region=region).get_client()

    def execute(self) -> CommandResult[VSI]:
        """
        Create a new VSI in the specified region using the provided template.

        Returns:
            CommandResult with the created VSI DTO on success, or error message on failure.
        """
        t = self.template
        self.log.info(
            f"Creating VSI name='{t.name}' profile='{t.profile}' "
            f"zone='{t.zone}' image='{t.image_id}' subnet='{t.subnet_id}'"
        )

        # Build the instance prototype payload for the IBM VPC API
        instance_prototype: dict[str, Any] = {
            "name": t.name,
            "zone": {"name": t.zone},
            "vpc": {"id": t.vpc_id},
            "profile": {"name": t.profile},
            "image": {"id": t.image_id},
            "primary_network_interface": {
                "subnet": {"id": t.subnet_id},
            },
        }

        # Attach SSH keys if provided
        if t.ssh_key_ids:
            instance_prototype["keys"] = [{"id": key_id} for key_id in t.ssh_key_ids]
            self.log.debug(f"Attaching {len(t.ssh_key_ids)} SSH key(s): {t.ssh_key_ids}")

        # Attach user data (cloud-init) if provided
        if t.user_data:
            instance_prototype["user_data"] = t.user_data
            self.log.debug("User data (cloud-init) attached")

        self.log.debug(f"Calling IBM VPC API create_instance for region='{self.region}'")
        try:
            resp: DetailedResponse = self.vpc_client.create_instance(
                instance_prototype=instance_prototype  # type: ignore[arg-type]
            )
        except Exception as e:
            self.log.error(f"Exception while creating VSI name='{t.name}': {e}")
            return CommandResult(success=False, message=f"Exception occurred while creating VSI: {e}")

        status = resp.get_status_code()
        if status != 201:
            self.log.warning(f"create_instance rejected (HTTP {status}): {resp.get_result()}")
            return CommandResult(success=False, message=f"Failed to create VSI: {resp.get_result()}")

        # Parse the response and build the VSI DTO
        data: dict[str, Any] = resp.get_result()  # type: ignore[assignment]
        vsi = VSI(
            id=data["id"],
            name=data["name"],
            status=data["status"],
            zone=data["zone"]["name"],
            cpu=data["vcpu"]["count"],
            ram=data["memory"] * 1024,
        )
        self.log.info(
            f"VSI created successfully: id='{vsi.id}' name='{vsi.name}' " f"status='{vsi.status}' zone='{vsi.zone}'"
        )
        return CommandResult(
            success=True,
            message=f"VSI '{vsi.name}' created successfully with id='{vsi.id}'.",
            data=vsi,
        )


# Made with Bob
