from enum import Enum
from django.db import models
from django.utils import timezone
from ninja import Schema


class OrgType(str, Enum):
    """an enum representing the type of organization"""

    DEMO = "demo"
    POC = "poc"
    CLIENT = "client"

    @classmethod
    def choices(cls):
        """django model definition needs an iterable for `choices`"""
        return [(key.value, key.name) for key in cls]


class OrgVizLoginType(str, Enum):
    """an enum for roles assignable to org-users"""

    BASIC_AUTH = "basic"
    GOOGLE_AUTH = "google"

    @classmethod
    def choices(cls):
        """django model definition needs an iterable for `choices`"""
        return [(key.value, key.name) for key in cls]


class TransformType(str, Enum):
    """an enum for transform type available either via ui or github"""

    UI = "ui"
    GIT = "github"


class OrgDbt(models.Model):
    """Docstring"""

    gitrepo_url = models.CharField(max_length=100, null=True)
    gitrepo_access_token_secret = models.CharField(
        max_length=100, null=True
    )  # skipcq: PTC-W0901, PTC-W0906

    project_dir = models.CharField(max_length=200)
    dbt_venv = models.CharField(max_length=200, null=True)

    target_type = models.CharField(max_length=10)
    default_schema = models.CharField(max_length=50)
    transform_type = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_created=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"OrgDbt[{self.gitrepo_url}|{self.target_type}|{self.default_schema}|{self.transform_type}]"


class Org(models.Model):
    """Docstring"""

    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=20, null=True)  # skipcq: PTC-W0901, PTC-W0906
    airbyte_workspace_id = models.CharField(  # skipcq: PTC-W0901, PTC-W0906
        max_length=36, null=True
    )
    dbt = models.ForeignKey(  # skipcq: PTC-W0901, PTC-W0906
        OrgDbt, on_delete=models.SET_NULL, null=True
    )
    viz_url = models.CharField(max_length=100, null=True)
    viz_login_type = models.CharField(
        choices=OrgVizLoginType.choices(), max_length=50, null=True
    )
    type = models.CharField(
        choices=OrgType.choices(), max_length=50, default=OrgType.CLIENT
    )
    ses_whitelisted_email = models.TextField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_created=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Org[{self.slug}|{self.name}|{self.airbyte_workspace_id}|{self.type}]"


class OrgSchema(Schema):
    """Docstring"""

    name: str
    slug: str = None
    airbyte_workspace_id: str = None
    viz_url: str = None
    viz_login_type: str = None
    tnc_accepted: bool = None
    is_demo: bool = False


class OrgWarehouse(models.Model):
    """A data warehouse for an org. Typically we expect exactly one"""

    wtype = models.CharField(max_length=25)  # postgres, bigquery, snowflake
    name = models.CharField(max_length=25, default="", blank=True)
    credentials = models.CharField(max_length=1000)
    org = models.ForeignKey(Org, on_delete=models.CASCADE)
    airbyte_destination_id = models.TextField(  # skipcq: PTC-W0901, PTC-W0906
        max_length=36, null=True
    )
    airbyte_docker_repository = models.TextField(  # skipcq: PTC-W0901, PTC-W0906
        max_length=100, null=True
    )
    airbyte_docker_image_tag = models.TextField(  # skipcq: PTC-W0901, PTC-W0906
        max_length=10, null=True
    )
    bq_location = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_created=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return (
            f"OrgWarehouse[{self.org.slug}|{self.wtype}|{self.airbyte_destination_id}]"
        )


class OrgWarehouseSchema(Schema):
    """payload to register an organization's data warehouse"""

    wtype: str
    name: str
    destinationDefId: str
    airbyteConfig: dict


# ============================================================================================
# new models to go away from blocks architecture


class OrgPrefectBlockv1(models.Model):
    """This containes the update version of the orgprefectblock model"""

    org = models.ForeignKey(Org, on_delete=models.CASCADE)
    block_type = models.CharField(max_length=25)  # all dbt blocks have the same type!
    block_id = models.CharField(max_length=36, unique=True)
    block_name = models.CharField(
        max_length=100, unique=True
    )  # use blockname to distinguish between different dbt commands
    created_at = models.DateTimeField(auto_created=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"OrgPrefectBlockv1[{self.org.name}|{self.block_type}|{self.block_name}]"


class OrgDataFlowv1(models.Model):
    """This contains the deployment id of an organization to schedule flows/pipelines"""

    org = models.ForeignKey(Org, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    deployment_name = models.CharField(  # skipcq: PTC-W0901, PTC-W0906
        max_length=100, null=True
    )
    deployment_id = models.CharField(  # skipcq: PTC-W0901, PTC-W0906
        max_length=36, unique=True, null=True
    )
    cron = models.CharField(max_length=36, null=True)  # skipcq: PTC-W0901, PTC-W0906

    dataflow_type = models.CharField(
        max_length=25,
        choices=(("orchestrate", "orchestrate"), ("manual", "manual")),
        default="orchestrate",
    )  # skipcq: PTC-W0901, PTC-W0906

    reset_conn_dataflow = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_created=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"OrgDataFlowv1[{self.name}|{self.deployment_name}|{self.deployment_id}|{self.cron}]"


class OrgSchemaChange(models.Model):
    """This contains the deployment id of an organization to schedule flows/pipelines"""

    org = models.ForeignKey(Org, on_delete=models.CASCADE)
    connection_id = models.CharField(max_length=36, unique=True, null=True)
    change_type = models.CharField(max_length=36, null=True)
    created_at = models.DateTimeField(auto_created=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
