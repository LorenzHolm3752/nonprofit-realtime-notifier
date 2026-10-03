from typing import Annotated, Literal

from pydantic import BaseModel, Field


class DonorReceipt(BaseModel):
    kind: Literal["donor_receipt"]
    channel: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    donor_name: str = Field(min_length=1)
    amount_cents: int = Field(gt=0)
    receipt_number: str = Field(min_length=1)


class VolunteerReminder(BaseModel):
    kind: Literal["volunteer_reminder"]
    channel: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    volunteer_name: str = Field(min_length=1)
    shift_starts_at: str = Field(min_length=1)
    location: str = Field(min_length=1)


class CampaignReport(BaseModel):
    kind: Literal["campaign_report"]
    channel: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    campaign_name: str = Field(min_length=1)
    raised_cents: int = Field(ge=0)
    donor_count: int = Field(ge=0)


Notification = Annotated[
    DonorReceipt | VolunteerReminder | CampaignReport,
    Field(discriminator="kind"),
]


class Delivery(BaseModel):
    channel: str
    event: str
    accepted: bool


def publication_for(notification: DonorReceipt | VolunteerReminder | CampaignReport) -> tuple[str, str, dict[str, object]]:
    if isinstance(notification, DonorReceipt):
        data = {
            "donor_name": notification.donor_name,
            "amount_cents": notification.amount_cents,
            "receipt_number": notification.receipt_number,
        }
        return notification.channel, "receipt.ready", data

    if isinstance(notification, VolunteerReminder):
        data = {
            "volunteer_name": notification.volunteer_name,
            "shift_starts_at": notification.shift_starts_at,
            "location": notification.location,
        }
        return notification.channel, "volunteer.shift_reminder", data

    data = {
        "campaign_name": notification.campaign_name,
        "raised_cents": notification.raised_cents,
        "donor_count": notification.donor_count,
    }
    return notification.channel, "campaign.report_ready", data
