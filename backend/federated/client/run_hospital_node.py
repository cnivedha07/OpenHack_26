import os
import sys
import argparse
import logging
import signal
import flwr as fl

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from federated.client.flower_client import HospitalFLClient

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [HospitalNode]: %(message)s")
logger = logging.getLogger("HospitalNode")


def main():
    parser = argparse.ArgumentParser(description="TrustFed 2.0 Standalone Hospital FL Node")
    parser.add_argument("--hospital-id", type=str, default=os.getenv("HOSPITAL_ID", "hospital_1"), help="Hospital ID (e.g. hospital_1)")
    parser.add_argument("--server-address", type=str, default=os.getenv("SERVER_ADDRESS", "127.0.0.1:8080"), help="Flower gRPC server address (e.g. 127.0.0.1:8080)")
    parser.add_argument("--data-dir", type=str, default=os.getenv("DATA_DIR", None), help="Path to synthetic_data directory")
    parser.add_argument("--tls", action="store_true", default=os.getenv("FL_TLS_ENABLED", "false").lower() == "true", help="Enable gRPC TLS encryption")

    args = parser.parse_args()

    logger.info(f"Starting standalone FL Node for '{args.hospital_id}' connecting to '{args.server_address}' (TLS: {args.tls})...")

    hospital_client = HospitalFLClient(hospital_id=args.hospital_id)
    if args.data_dir:
        from federated.data_loader import get_hospital_dataloader
        hospital_client.dataloader = get_hospital_dataloader(args.hospital_id, data_dir=args.data_dir)

    def handle_signal(sig, frame):
        logger.info(f"Received signal {sig}. Shutting down hospital node gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Convert NumPyClient to Client if flwr version requires to_client()
    fl_client = hospital_client.to_client() if hasattr(hospital_client, "to_client") else hospital_client

    root_certificates = None
    if args.tls:
        cert_path = os.getenv("FL_CA_CERT_PATH", "certs/ca.crt")
        if os.path.exists(cert_path):
            with open(cert_path, "rb") as f:
                root_certificates = f.read()

    try:
        if hasattr(fl.client, "start_numpy_client"):
            fl.client.start_numpy_client(
                server_address=args.server_address,
                client=hospital_client,
                root_certificates=root_certificates
            )
        else:
            fl.client.start_client(
                server_address=args.server_address,
                client=fl_client,
                root_certificates=root_certificates
            )
    except Exception as e:
        logger.error(f"FL Client error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
