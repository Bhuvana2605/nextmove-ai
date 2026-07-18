import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError


class MemoryStore:

    TABLE_NAME = "nextmove-memory"

    def __init__(self, table_name: str | None = None):
        region = os.getenv("AWS_DEFAULT_REGION")
        self.table_name = table_name or self.TABLE_NAME
        self._resource = boto3.resource("dynamodb", region_name=region)
        self._table = self._resource.Table(self.table_name)

    def save_recommendation(self, user_id, opportunity):
        try:
            self._table.put_item(
                Item={
                    "user_id": str(user_id),
                    "opportunity_id": str(opportunity.id),
                    "title": getattr(opportunity, "title", ""),
                    "source": getattr(opportunity, "source", ""),
                    "url": getattr(opportunity, "url", ""),
                    "recommended_at": datetime.now(timezone.utc).isoformat(),
                }
            )
            return True
        except ClientError:
            return False

    def was_recommended(self, user_id, opportunity_id) -> bool:
        try:
            response = self._table.get_item(
                Key={
                    "user_id": str(user_id),
                    "opportunity_id": str(opportunity_id),
                }
            )
            return "Item" in response
        except ClientError:
            return False

    def filter_new(self, user_id, opportunities):
        try:
            return [
                opportunity
                for opportunity in opportunities
                if not self.was_recommended(user_id, getattr(opportunity, "id", ""))
            ]
        except ClientError as e:
            print(f"DynamoDB Error: {e}")
            return []