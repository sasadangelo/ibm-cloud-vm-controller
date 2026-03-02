# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from pydantic import BaseModel, Field


class VSITemplate(BaseModel):
    """
    Template for creating a new Virtual Server Instance (VSI) on IBM Cloud VPC.

    All required fields must be provided. Optional fields have sensible defaults.
    IBM Cloud resource IDs (vpc_id, subnet_id, image_id, profile) can be retrieved
    via the IBM Cloud Console or CLI.
    """

    name: str = Field(
        description="Name for the new VSI (must be unique within the VPC, lowercase alphanumeric and hyphens)"
    )
    zone: str = Field(description="Availability zone where the VSI will be created (e.g. 'us-east-1', 'eu-de-1')")
    vpc_id: str = Field(description="ID of the VPC in which to create the VSI")
    subnet_id: str = Field(description="ID of the subnet to attach the VSI's primary network interface to")
    image_id: str = Field(description="ID of the OS image to use (e.g. ibm-ubuntu-22-04-minimal-amd64)")
    profile: str = Field(
        default="bx2-2x8", description="VSI profile name defining CPU and RAM (e.g. 'bx2-2x8' = 2 vCPU / 8 GB RAM)"
    )
    ssh_key_ids: list[str] = Field(
        default_factory=list, description="List of SSH key IDs to inject into the VSI for access"
    )
    user_data: str | None = Field(default=None, description="Optional cloud-init user data script to run on first boot")


# Made with Bob
