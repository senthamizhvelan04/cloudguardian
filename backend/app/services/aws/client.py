import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings

log = logging.getLogger(__name__)


class AWSService:
    def __init__(self) -> None:
        s = get_settings()

        self.enabled = s.aws_enabled
        self.region = s.aws_region
        self.ssm_timeout = s.aws_ssm_timeout_seconds

        if self.enabled:
            self.ec2 = boto3.client(
                "ec2",
                region_name=self.region,
            )
            self.cloudwatch = boto3.client(
                "cloudwatch",
                region_name=self.region,
            )
            self.ssm = boto3.client(
                "ssm",
                region_name=self.region,
            )
        else:
            self.ec2 = None
            self.cloudwatch = None
            self.ssm = None

    def status(self, instance_id: str) -> dict[str, Any]:
        if not self.enabled:
            return {
                "instance_id": instance_id,
                "state": "mock",
                "enabled": False,
            }

        try:
            response = self.ec2.describe_instances(
                InstanceIds=[instance_id]
            )

            instance = response["Reservations"][0]["Instances"][0]

            return {
                "instance_id": instance_id,
                "state": instance["State"]["Name"],
                "instance_type": instance.get("InstanceType"),
                "private_ip": instance.get("PrivateIpAddress"),
                "public_ip": instance.get("PublicIpAddress"),
            }

        except (ClientError, BotoCoreError) as exc:
            log.exception("EC2 status failed")
            raise RuntimeError(str(exc)) from exc

    def cpu(
        self,
        instance_id: str,
        minutes: int = 15,
    ) -> float | None:
        if not self.enabled:
            return None

        response = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[
                {
                    "Name": "InstanceId",
                    "Value": instance_id,
                }
            ],
            StartTime=datetime.now(UTC) - timedelta(minutes=minutes),
            EndTime=datetime.now(UTC),
            Period=300,
            Statistics=["Average"],
        )

        points = response.get("Datapoints", [])

        if not points:
            return None

        latest = max(
            points,
            key=lambda point: point["Timestamp"],
        )

        return round(latest["Average"], 2)

    def send_ssm(
        self,
        instance_id: str,
        action: str,
    ) -> str:
        s = get_settings()
        container_name = getattr(s, "container_name", "cloudguardian")
        port = getattr(s, "health_check_port", 8000)

        commands = {
            "restart_service": (
                f"sudo docker restart {container_name}"
            ),
            "inspect_and_restart_service": (
                f"sudo docker ps "
                f"--filter name={container_name} "
                "--format '{{{{.Names}}}}' "
                f"| grep -q {container_name} "
                f"&& sudo docker restart {container_name} "
                f"|| sudo docker start {container_name}"
            ),
            "collect_logs": (
                f"sudo docker logs --tail 100 {container_name}"
            ),
            "verify_recovery": (
                f"sudo docker inspect "
                f"-f '{{{{.State.Running}}}}' {container_name} "
                f"&& curl -fsS http://localhost:{port}/health"
            ),
        }

        if action not in commands:
            raise ValueError("Action is not allowlisted")

        if not self.enabled:
            return "mock-command-id"

        try:
            response = self.ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName=get_settings().aws_ssm_document,
                Parameters={
                    "commands": [commands[action]]
                },
                TimeoutSeconds=self.ssm_timeout,
            )

            return response["Command"]["CommandId"]

        except (ClientError, BotoCoreError) as exc:
            log.exception("SSM command failed")
            raise RuntimeError(str(exc)) from exc

    def get_ssm_command_status(
        self,
        command_id: str,
        instance_id: str,
    ) -> dict[str, Any]:
        if not self.enabled:
            return {
                "status": "Success",
                "stdout": "mock-success",
                "stderr": "",
            }

        try:
            response = self.ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id,
            )

            return {
                "status": response["Status"],
                "stdout": response.get(
                    "StandardOutputContent",
                    "",
                ),
                "stderr": response.get(
                    "StandardErrorContent",
                    "",
                ),
            }

        except (ClientError, BotoCoreError) as exc:
            log.exception(
                "SSM command status check failed"
            )
            raise RuntimeError(str(exc)) from exc

    def wait_for_ssm_command(
        self,
        command_id: str,
        instance_id: str,
        max_wait_seconds: int = 60,
        poll_interval: int = 5,
    ) -> dict[str, Any]:
        if not self.enabled:
            return {
                "status": "Success",
                "stdout": "mock-success",
                "stderr": "",
            }

        elapsed = 0

        # NOTE: time.sleep() blocks the thread, but since FastAPI endpoints
        # run in a threadpool (sync def), this does not block the async event loop.
        while elapsed < max_wait_seconds:
            result = self.get_ssm_command_status(
                command_id,
                instance_id,
            )

            status = result["status"]

            if status == "Success":
                return result

            if status in {
                "Failed",
                "Cancelled",
                "TimedOut",
            }:
                return result

            time.sleep(poll_interval)
            elapsed += poll_interval

        return {
            "status": "Timeout",
            "stdout": "",
            "stderr": (
                "SSM command did not complete "
                "within the allowed time."
            ),
        }

    def verify_recovery(
        self,
        instance_id: str,
    ) -> dict[str, Any]:
        command_id = self.send_ssm(
            instance_id,
            "verify_recovery",
        )

        result = self.wait_for_ssm_command(
            command_id,
            instance_id,
            max_wait_seconds=30,
            poll_interval=5,
        )

        if result["status"] == "Success":
            return {
                "success": True,
                "command_id": command_id,
                "status": result["status"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
            }

        return {
            "success": False,
            "command_id": command_id,
            "status": result["status"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        }

