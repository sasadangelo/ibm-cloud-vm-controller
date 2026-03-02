# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
import os
from dotenv import load_dotenv
from dtos import VSI, VSITemplate
from services import CommandResult, VSIController

# Load environment variables from .env
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration — edit these values or set them in your .env file
# ---------------------------------------------------------------------------
REGION = os.environ.get("IBM_REGION", "us-east")
VPC_ID = os.environ.get("VPC_ID", "<your-vpc-id>")
SUBNET_ID = os.environ.get("SUBNET_ID", "<your-subnet-id>")
IMAGE_ID = os.environ.get("IMAGE_ID", "<your-image-id>")
SSH_KEY_ID = os.environ.get("SSH_KEY_ID", "")
PROFILE = os.environ.get("VSI_PROFILE", "bx2-2x8")
VM_NAME = "test-vm"


def print_vsi_list(vsi_list: list[VSI]) -> None:
    """Prints the list of VSI objects in a human-readable format."""
    print(f"  Retrieved {len(vsi_list)} VSI(s):")
    for vsi in vsi_list:
        print(
            f"  - ID: {vsi.id}, Name: {vsi.name}, Status: {vsi.status}, "
            f"Zone: {vsi.zone}, CPU: {vsi.cpu}, RAM: {vsi.ram}MB"
        )


def main() -> None:
    controller: VSIController = VSIController(region=REGION)

    # -----------------------------------------------------------------------
    # Step 1: Create the VSI
    # -----------------------------------------------------------------------
    print(f"\n🏗️  Creating VSI '{VM_NAME}' in region '{REGION}'...")
    template = VSITemplate(
        name=VM_NAME,
        zone=f"{REGION}-2",
        vpc_id=VPC_ID,
        subnet_id=SUBNET_ID,
        image_id=IMAGE_ID,
        profile=PROFILE,
        ssh_key_ids=[SSH_KEY_ID] if SSH_KEY_ID else [],
    )
    create_result: CommandResult[VSI] = controller.create_vsi(template=template)
    if not create_result.success or not create_result.data:
        print(f"❌ Failed to create VSI: {create_result.message}")
        return
    vsi: VSI = create_result.data
    print(f"✅ VSI created: id='{vsi.id}' status='{vsi.status}'")

    # -----------------------------------------------------------------------
    # Step 2: List all VSIs
    # -----------------------------------------------------------------------
    print(f"\n📋 Listing all VSIs in region '{REGION}'...")
    list_result_1: CommandResult[list[VSI]] = controller.list_vsi()
    if list_result_1.success and list_result_1.data:
        print_vsi_list(vsi_list=list_result_1.data)
    else:
        print(f"❌ Failed to list VSIs: {list_result_1.message}")

    # -----------------------------------------------------------------------
    # Step 3: Stop the VSI
    # -----------------------------------------------------------------------
    print(f"\n🛑 Stopping VSI '{VM_NAME}' (id='{vsi.id}')...")
    stop_result: CommandResult[str | None] = controller.stop_vsi(vsi_id=vsi.id)
    if stop_result.success:
        print(f"✅ {stop_result.message}")
    else:
        print(f"❌ {stop_result.message}")

    # -----------------------------------------------------------------------
    # Step 4: Start the VSI again
    # -----------------------------------------------------------------------
    print(f"\n🚀 Starting VSI '{VM_NAME}' (id='{vsi.id}')...")
    start_result: CommandResult[str | None] = controller.start_vsi(vsi_id=vsi.id)
    if start_result.success:
        print(f"✅ {start_result.message}")
    else:
        print(f"❌ {start_result.message}")

    # -----------------------------------------------------------------------
    # Step 5: List all VSIs again
    # -----------------------------------------------------------------------
    print(f"\n📋 Listing all VSIs in region '{REGION}' after restart...")
    list_result_2: CommandResult[list[VSI]] = controller.list_vsi()
    if list_result_2.success and list_result_2.data:
        print_vsi_list(vsi_list=list_result_2.data)
    else:
        print(f"❌ Failed to list VSIs: {list_result_2.message}")

    # -----------------------------------------------------------------------
    # Step 6: Delete the VSI
    # Note: IBM Cloud requires the VSI to be stopped before deletion.
    #       Stop it again to ensure it is in the correct state.
    # -----------------------------------------------------------------------
    print(f"\n🛑 Stopping VSI '{VM_NAME}' before deletion...")
    controller.stop_vsi(vsi_id=vsi.id)

    print(f"\n🗑️  Deleting VSI '{VM_NAME}' (id='{vsi.id}')...")
    delete_result: CommandResult[str | None] = controller.delete_vsi(vsi_id=vsi.id)
    if delete_result.success:
        print(f"✅ {delete_result.message}")
    else:
        print(f"❌ {delete_result.message}")

    print("\n🏁 Done.")


if __name__ == "__main__":
    main()
