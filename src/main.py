# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
from dtos import VSI
from services import CommandResult, VSIController


def print_vsi_list(vsi_list: list[VSI]) -> None:
    """Prints the list of VSI objects in a human-readable format."""
    print(f"Retrieved {len(vsi_list)} VSI(s):")
    for vsi in vsi_list:
        print(
            f"- ID: {vsi.id}, Name: {vsi.name}, Status: {vsi.status}, Zone: {vsi.zone}, "
            f"CPU: {vsi.cpu}, RAM: {vsi.ram}MB"
        )


def main() -> None:
    controller: VSIController = VSIController(region="us-east")

    # List all VSIs
    list_result_1: CommandResult[list[VSI]] = controller.list_vsi()

    if list_result_1.success:
        if list_result_1.data:
            print_vsi_list(vsi_list=list_result_1.data)
        else:
            print(f"No VSI found: {list_result_1.message}")
            return
    else:
        print(f"❌ Failed to retrieve VSI list: {list_result_1.message}")
        return

    # Optional: Find a VSI by name and stop/start it
    target_name = "matteo-test"
    vsi: VSI | None = next((v for v in list_result_1.data if v.name == target_name), None)

    if not vsi:
        print(f"⚠️  VSI with name '{target_name}' not found.")
        return

    # Stop the VSI
    stop_result: CommandResult[str | None] = controller.stop_vsi(vsi_id=vsi.id)
    print(f"🛑 Stop result: {stop_result.message}")

    # Start the VSI again
    start_result: CommandResult[str | None] = controller.start_vsi(vsi_id=vsi.id)
    print(f"🚀 Start result: {start_result.message}")

    # List all VSIs
    list_result_2: CommandResult[list[VSI]] = controller.list_vsi()

    if list_result_2.success and list_result_2.data:
        print_vsi_list(vsi_list=list_result_2.data)
    else:
        print(f"❌ Failed to retrieve VSI list: {list_result_2.message}")
        return


if __name__ == "__main__":
    main()
