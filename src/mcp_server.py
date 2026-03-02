# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from typing import Annotated, Any
from mcp.server.fastmcp import FastMCP
from core import LoggerManager, setup_logging, vsi_controller_config
from dtos import VSI
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


if __name__ == "__main__":
    log.info("IBM Cloud VM Controller MCP server is starting...")
    mcp.run()
    log.info("IBM Cloud VM Controller MCP server has stopped.")

# Made with Bob
