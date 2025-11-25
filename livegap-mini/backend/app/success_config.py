from enum import Enum


class Goal(str, Enum):
    TALK_TO_SALES = "talk_to_sales"
    PRICING = "pricing"
    SIGN_UP = "sign_up"
    HELP = "help"
    CUSTOMERS = "customers"


START_URLS = {
    "intercom": "https://www.intercom.com/suite",
    "hubspot": "https://www.hubspot.com/",
    "asana": "https://asana.com/",
    "calendly": "https://calendly.com/",
    "notion": "https://www.notion.so/",
    "airtable": "https://www.airtable.com/",
    "zendesk": "https://www.zendesk.com/",
    "atlassian_jira": "https://www.atlassian.com/software/jira",
    "monday": "https://monday.com/",
    "slack": "https://slack.com/",
}

SUCCESS_URLS = {
    "intercom": {
        Goal.TALK_TO_SALES: ["https://www.intercom.com/contact-sales"],
        Goal.PRICING: ["https://www.intercom.com/pricing"],
        Goal.SIGN_UP: ["https://app.intercom.com/admins/sign_up"],
        Goal.HELP: ["https://www.intercom.com/help"],
        Goal.CUSTOMERS: ["https://www.intercom.com/customers"],
    },
    "hubspot": {
        Goal.TALK_TO_SALES: ["https://offers.hubspot.com/contact-sales"],
        Goal.PRICING: ["https://www.hubspot.com/pricing"],
        Goal.SIGN_UP: ["https://app.hubspot.com/signup-hubspot"],
        Goal.HELP: ["https://help.hubspot.com/"],
        Goal.CUSTOMERS: ["https://www.hubspot.com/case-studies"],
    },
    "asana": {
        Goal.TALK_TO_SALES: ["https://asana.com/sales"],
        Goal.PRICING: ["https://asana.com/pricing"],
        Goal.SIGN_UP: ["https://asana.com/create-account"],
        Goal.HELP: ["https://help.asana.com/s"],
        Goal.CUSTOMERS: ["https://asana.com/customers"],
    },
    "calendly": {
        Goal.TALK_TO_SALES: ["https://calendly.com/contact"],
        Goal.PRICING: ["https://calendly.com/pricing"],
        Goal.SIGN_UP: ["https://calendly.com/signup"],
        Goal.HELP: ["https://help.calendly.com/hc"],
        Goal.CUSTOMERS: ["https://calendly.com/customers"],
    },
    "notion": {
        Goal.TALK_TO_SALES: ["https://www.notion.com/contact-sales"],
        Goal.PRICING: ["https://www.notion.com/pricing"],
        Goal.SIGN_UP: ["https://www.notion.so/signup"],
        Goal.HELP: ["https://www.notion.com/help"],
        Goal.CUSTOMERS: [],  # no customers page -> always fail for this goal
    },
    "airtable": {
        Goal.TALK_TO_SALES: ["https://www.airtable.com/contact-sales"],
        Goal.PRICING: ["https://airtable.com/pricing"],
        Goal.SIGN_UP: ["https://airtable.com/signup"],
        Goal.HELP: ["https://www.airtable.com/lp/resources"],
        Goal.CUSTOMERS: ["https://www.airtable.com/customer-stories"],
    },
    "zendesk": {
        Goal.TALK_TO_SALES: ["https://www.zendesk.com/contact/"],
        Goal.PRICING: ["https://www.zendesk.com/pricing/"],
        Goal.SIGN_UP: ["https://www.zendesk.com/register/"],
        Goal.HELP: ["https://support.zendesk.com/hc"],
        Goal.CUSTOMERS: ["https://www.zendesk.com/why-zendesk/customers/"],
    },
    "atlassian_jira": {
        Goal.TALK_TO_SALES: [],  # intentionally unreachable
        Goal.PRICING: ["https://www.atlassian.com/software/jira/pricing"],
        Goal.SIGN_UP: ["https://www.atlassian.com/try/cloud/signup"],
        Goal.HELP: ["https://support.atlassian.com/"],
        Goal.CUSTOMERS: [],  # intentionally unreachable
    },
    "monday": {
        Goal.TALK_TO_SALES: ["https://monday.com/sales/contact-us"],
        Goal.PRICING: ["https://monday.com/pricing"],
        Goal.SIGN_UP: ["https://auth.monday.com/users/sign_up_new"],
        Goal.HELP: ["https://support.monday.com/hc"],
        Goal.CUSTOMERS: ["https://monday.com/w/customer-stories"],
    },
    "slack": {
        Goal.TALK_TO_SALES: ["https://slack.com/contact-sales"],
        Goal.PRICING: ["https://slack.com/pricing"],
        Goal.SIGN_UP: ["https://slack.com/get-started"],
        Goal.HELP: ["https://slack.com/help"],
        Goal.CUSTOMERS: ["https://slack.com/customer-stories"],
    },
}