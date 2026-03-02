# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from typing import Annotated, Any
from mcp.server.fastmcp import FastMCP
from core import LoggerManager, setup_logging, vsi_controller_config
from dtos import VSI, VSITemplate
from services import VSIController
from services.commands.base import CommandResult

# Initialize logging from config
setup_logging(
    level=vsi_controller_config.log.level,
    console=vsi_controller_config.log.console,
    file=vsi_controller_config.log.file,
    rotation=vsi_controller_config.log.rotation,
    retention=vsi_controller_config.log.retention,
    compression=vsi_controller_config.log.compression,
)

# Module-level logger
log = LoggerManager.get_logger("MCPServer")

# Create the MCP server
mcp: FastMCP[Any] = FastMCP(name="ibm_vm_controller")


@mcp.tool()
def list_vsi(
    region: Annotated[str, "IBM Cloud region (e.g. 'us-south', 'us-east', 'eu-de')"],
) -> list[dict]:
    """List all Virtual Server Instances (VSIs) in the given IBM Cloud region.

    Returns a list of VSIs, each with: id, name, status, zone, cpu, ram.
    """
    log.info(f"Tool 'list_vsi' called for region='{region}'")
    controller: VSIController = VSIController(region=region)
    result: CommandResult[list[VSI]] = controller.list_vsi()
    if not result.success or not result.data:
        log.error(f"list_vsi failed for region='{region}': {result.message}")
        raise RuntimeError(result.message)
    log.info(f"list_vsi returned {len(result.data)} VSI(s) for region='{region}'")
    return [vsi.model_dump() for vsi in result.data]


@mcp.tool()
def start_vsi(
    region: Annotated[str, "IBM Cloud region (e.g. 'us-south', 'us-east', 'eu-de')"],
    vsi_id: Annotated[str, "The ID of the VSI to start"],
) -> str:
    """Start a specific Virtual Server Instance (VSI) given its ID and region."""
    log.info(f"Tool 'start_vsi' called for vsi_id='{vsi_id}' in region='{region}'")
    controller: VSIController = VSIController(region=region)
    result: CommandResult[str | None] = controller.start_vsi(vsi_id=vsi_id)
    if not result.success:
        log.error(f"start_vsi failed for vsi_id='{vsi_id}': {result.message}")
        raise RuntimeError(result.message)
    log.info(f"start_vsi succeeded for vsi_id='{vsi_id}': {result.message}")
    return result.message


@mcp.tool()
def stop_vsi(
    region: Annotated[str, "IBM Cloud region (e.g. 'us-south', 'us-east', 'eu-de')"],
    vsi_id: Annotated[str, "The ID of the VSI to stop"],
) -> str:
    """Stop a specific Virtual Server Instance (VSI) given its ID and region."""
    log.info(f"Tool 'stop_vsi' called for vsi_id='{vsi_id}' in region='{region}'")
    controller: VSIController = VSIController(region=region)
    result: CommandResult[str | None] = controller.stop_vsi(vsi_id=vsi_id)
    if not result.success:
        log.error(f"stop_vsi failed for vsi_id='{vsi_id}': {result.message}")
        raise RuntimeError(result.message)
    log.info(f"stop_vsi succeeded for vsi_id='{vsi_id}': {result.message}")
    return result.message


@mcp.tool()
def create_vsi(
    region: Annotated[str, "IBM Cloud region (e.g. 'us-south', 'us-east', 'eu-de')"],
    name: Annotated[str, "Name for the new VSI (lowercase alphanumeric and hyphens)"],
    zone: Annotated[str, "Availability zone (e.g. 'us-east-1', 'eu-de-1')"],
    vpc_id: Annotated[str, "ID of the VPC in which to create the VSI"],
    subnet_id: Annotated[str, "ID of the subnet for the primary network interface"],
    image_id: Annotated[str, "ID of the OS image to use"],
    profile: Annotated[str, "VSI profile name (e.g. 'bx2-2x8' = 2 vCPU / 8 GB RAM)"] = "bx2-2x8",
    ssh_key_ids: Annotated[list[str], "List of SSH key IDs to inject into the VSI"] = [],
    user_data: Annotated[str | None, "Optional cloud-init user data script"] = None,
) -> dict:
    """Create a new Virtual Server Instance (VSI) in the given IBM Cloud region.

    Returns the created VSI with: id, name, status, zone, cpu, ram.
    """
    log.info(f"Tool 'create_vsi' called: name='{name}' region='{region}' zone='{zone}' profile='{profile}'")
    template = VSITemplate(
        name=name,
        zone=zone,
        vpc_id=vpc_id,
        subnet_id=subnet_id,
        image_id=image_id,
        profile=profile,
        ssh_key_ids=ssh_key_ids,
        user_data=user_data,
    )
    controller: VSIController = VSIController(region=region)
    result: CommandResult[VSI] = controller.create_vsi(template=template)
    if not result.success or not result.data:
        log.error(f"create_vsi failed for name='{name}': {result.message}")
        raise RuntimeError(result.message)
    log.info(f"create_vsi succeeded: id='{result.data.id}' name='{result.data.name}'")
    return result.data.model_dump()


@mcp.tool()
def delete_vsi(
    region: Annotated[str, "IBM Cloud region (e.g. 'us-south', 'us-east', 'eu-de')"],
    vsi_id: Annotated[str, "The ID of the VSI to delete"],
) -> str:
    """Delete a specific Virtual Server Instance (VSI) given its ID and region.

    The VSI must be in 'stopped' state before deletion.
    """
    log.info(f"Tool 'delete_vsi' called for vsi_id='{vsi_id}' in region='{region}'")
    controller: VSIController = VSIController(region=region)
    result: CommandResult[str | None] = controller.delete_vsi(vsi_id=vsi_id)
    if not result.success:
        log.error(f"delete_vsi failed for vsi_id='{vsi_id}': {result.message}")
        raise RuntimeError(result.message)
    log.info(f"delete_vsi succeeded for vsi_id='{vsi_id}': {result.message}")
    return result.message


if __name__ == "__main__":
    log.info("IBM Cloud VM Controller MCP server is starting...")
    mcp.run()
    log.info("IBM Cloud VM Controller MCP server has stopped.")

# Made with Bob
