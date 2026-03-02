# -----------------------------------------------------------------------------
# Copyright (c) 2026 Salvatore D'Angelo, Code4Projects
# Licensed under the MIT License. See LICENSE.md for details.
# -----------------------------------------------------------------------------
import os
from typing import Optional
from dotenv import load_dotenv
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_vpc import VpcV1


class IBMVPCClient:
    """
    Singleton class responsible for creating and managing a single instance
    of the IBM VPC client (`VpcV1`) authenticated with an API key.

    Usage:
        - The first instantiation must provide a `region` (e.g. "us-south").
        - Subsequent instantiations will return the same instance.
        - The client is reused across the application to avoid redundant authentication/setup.
    """

    # Class-level reference to the singleton instance
    _instance: Optional["IBMVPCClient"] = None

    def __new__(cls, region: str | None = None):
        """
        Ensures only one instance of the client is created.
        Requires `region` on the first instantiation to properly configure the client.

        :param region: IBM Cloud region code (e.g. "us-south")
        :raises ValueError: if no region is provided on the first use
        """
        if cls._instance is None:
            if not region:
                raise ValueError("First instantiation of IBMVPCClient must include a region (e.g., 'us-south').")
            # Create the singleton instance and initialize it
            cls._instance = super().__new__(cls)
            cls._instance._init(region)
        return cls._instance

    def _init(self, region: str) -> None:
        """
        Internal initialization logic for setting up the authenticated VPC client.

        :param region: The IBM Cloud region to target (e.g. "eu-de", "us-south")
        :raises ValueError: if API_KEY is missing from the environment
        """
        # Load environment variables from .env
        load_dotenv()
        # Read the API key required to authenticate with IBM Cloud
        api_key: str | None = os.environ.get("API_KEY")
        if not api_key:
            raise ValueError("API_KEY not set in environment variables")
        # Set up the IBM IAM authenticator using the API key
        authenticator: IAMAuthenticator = IAMAuthenticator(apikey=api_key)
        # Create the VPC client with the authenticator
        self.client = VpcV1(authenticator=authenticator)
        # Set the correct service URL for the given region
        self.client.set_service_url(service_url=f"https://{region}.iaas.cloud.ibm.com/v1")

    def get_client(self) -> VpcV1:
        """
        Returns the initialized VPC client instance.

        :return: Authenticated VpcV1 client
        """
        return self.client
