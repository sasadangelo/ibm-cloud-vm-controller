# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
import os
from typing import Annotated, Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from dtos import VSI
from services import VSIController
from services.commands.base import CommandResult

# Load environment variables from .env
load_dotenv()

# Read region from environment — must be set in .env alongside API_KEY
_region: str = os.environ.get("IBM_REGION", "us-south")

# Instantiate the controller once at startup (singleton VPC client underneath)
controller: VSIController = VSIController(region=_region)

# Create the MCP server
mcp: FastMCP[Any] = FastMCP(name="ibm_vm_controller")


@mcp.tool()
def list_vsi() -> list[dict]:
    """List all Virtual Server Instances (VSIs) in the IBM Cloud account.

    Returns a list of VSIs, each with: id, name, status, zone, cpu, ram.
    """
    result: CommandResult[list[VSI]] = controller.list_vsi()
    if not result.success or not result.data:
        raise RuntimeError(result.message)
    return [vsi.model_dump() for vsi in result.data]


@mcp.tool()
def start_vsi(vsi_id: Annotated[str, "The ID of the VSI to start"]) -> str:
    """Start a specific Virtual Server Instance (VSI) given its ID."""
    result: CommandResult[str | None] = controller.start_vsi(vsi_id=vsi_id)
    if not result.success:
        raise RuntimeError(result.message)
    return result.message


@mcp.tool()
def stop_vsi(vsi_id: Annotated[str, "The ID of the VSI to stop"]) -> str:
    """Stop a specific Virtual Server Instance (VSI) given its ID."""
    result: CommandResult[str | None] = controller.stop_vsi(vsi_id=vsi_id)
    if not result.success:
        raise RuntimeError(result.message)
    return result.message


if __name__ == "__main__":
    mcp.run()

# Made with Bob
