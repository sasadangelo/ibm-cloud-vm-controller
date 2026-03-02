# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
import os
from dotenv import load_dotenv
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_vpc import VpcV1
from core import LoggerManager

_log = LoggerManager.get_logger("IBMVPCClient")


class IBMVPCClient:
    """
    Factory class that creates and caches one VPC client per IBM Cloud region.

    Usage:
        client = IBMVPCClient(region="us-east").get_client()

    The first call for a given region authenticates and builds the VpcV1 client.
    Subsequent calls for the same region return the cached client.
    """

    # Class-level cache: region -> VpcV1 client
    _clients: dict[str, VpcV1] = {}

    def __init__(self, region: str) -> None:
        """
        Ensure a VPC client exists for the given region.

        :param region: IBM Cloud region code (e.g. "us-south", "us-east", "eu-de")
        :raises ValueError: if API_KEY is missing from the environment
        """
        if region not in IBMVPCClient._clients:
            _log.debug(f"No cached client for region='{region}', building a new one...")
            IBMVPCClient._clients[region] = self._build_client(region)
        else:
            _log.debug(f"Reusing cached VPC client for region='{region}'")
        self._region = region

    def _build_client(self, region: str) -> VpcV1:
        """
        Build and return an authenticated VpcV1 client for the given region.

        :param region: The IBM Cloud region to target
        :raises ValueError: if API_KEY is not set in the environment
        """
        # Load environment variables from .env
        load_dotenv()
        # Read the API key required to authenticate with IBM Cloud
        api_key: str | None = os.environ.get("API_KEY")
        if not api_key:
            _log.error("API_KEY not found in environment variables")
            raise ValueError("API_KEY not set in environment variables")
        # Set up the IBM IAM authenticator using the API key
        authenticator: IAMAuthenticator = IAMAuthenticator(apikey=api_key)
        # Create the VPC client with the authenticator
        client = VpcV1(authenticator=authenticator)
        # Set the correct service URL for the given region
        service_url = f"https://{region}.iaas.cloud.ibm.com/v1"
        client.set_service_url(service_url=service_url)
        _log.info(f"VPC client built for region='{region}' → {service_url}")
        return client

    def get_client(self) -> VpcV1:
        """
        Returns the cached VPC client for this instance's region.

        :return: Authenticated VpcV1 client
        """
        return IBMVPCClient._clients[self._region]


# Made with Bob
