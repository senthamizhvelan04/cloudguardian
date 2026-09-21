import logging
from datetime import UTC
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
            self.ec2 = boto3.client("ec2", region_name=self.region)
            self.cloudwatch = boto3.client("cloudwatch", region_name=self.region)
            self.ssm = boto3.client("ssm", region_name=self.region)
        else:
            self.ec2 = self.cloudwatch = self.ssm = None

    def status(self, instance_id: str) -> dict[str, Any]:
        if not self.enabled:
            return {"instance_id": instance_id, "state": "mock", "enabled": False}
        try:
            r = self.ec2.describe_instances(InstanceIds=[instance_id])
            i = r["Reservations"][0]["Instances"][0]
            return {
                "instance_id": instance_id,
                "state": i["State"]["Name"],
                "instance_type": i.get("InstanceType"),
                "private_ip": i.get("PrivateIpAddress"),
                "public_ip": i.get("PublicIpAddress"),
            }
        except (ClientError, BotoCoreError) as exc:
            log.exception("EC2 status failed")
            raise RuntimeError(str(exc)) from exc

    def cpu(self, instance_id: str, minutes: int = 15) -> float | None:
        if not self.enabled:
            return None
        from datetime import datetime, timedelta
        r = self.cloudwatch.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=datetime.now(UTC) - timedelta(minutes=minutes),
            EndTime=datetime.now(UTC),
            Period=300,
            Statistics=["Average"],
        )
        points = r.get("Datapoints", [])
        return round(points[-1]["Average"], 2) if points else None

    def send_ssm(self, instance_id: str, action: str) -> str:
        commands = {
            "restart_service": "sudo systemctl restart cloudguardian-test.service",
            "inspect_and_restart_service": "sudo systemctl is-active cloudguardian-test.service || sudo systemctl start cloudguardian-test.service",
            "collect_logs": "sudo journalctl -u cloudguardian-test.service -n 100 --no-pager",
            "verify_recovery": "systemctl is-active cloudguardian-test.service",
        }
        if action not in commands:
            raise ValueError("Action is not allowlisted")
        if not self.enabled:
            return "mock-command-id"
        r = self.ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName=get_settings().aws_ssm_document,
            Parameters={"commands": [commands[action]]},
            TimeoutSeconds=self.ssm_timeout,
        )
        return r["Command"]["CommandId"]
