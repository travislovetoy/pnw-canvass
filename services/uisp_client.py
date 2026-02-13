import requests
from flask import current_app


def get_service_plans():
    """Fetch service plans from UISP CRM."""
    base = current_app.config["UISP_BASE_URL"].rstrip("/")
    token = current_app.config["UISP_API_TOKEN"]
    if not token:
        return []

    try:
        resp = requests.get(
            f"{base}/service-plans",
            headers={"x-auth-token": token},
            timeout=10,
            verify=True,
        )
        resp.raise_for_status()
        plans = resp.json()
        # Return non-archived plans with useful fields
        result = []
        for p in plans:
            if p.get("archived"):
                continue
            # Get monthly price from periods
            price = None
            for period in (p.get("periods") or []):
                if period.get("period") == 1 and period.get("enabled") and period.get("price") is not None:
                    price = period["price"]
                    break
            result.append({
                "id": p["id"],
                "name": p["name"],
                "downloadSpeed": p.get("downloadSpeed"),
                "uploadSpeed": p.get("uploadSpeed"),
                "price": price,
            })
        return result
    except requests.RequestException:
        return []


def push_lead_to_uisp(lead):
    base = current_app.config["UISP_BASE_URL"].rstrip("/")
    token = current_app.config["UISP_API_TOKEN"]
    if not token:
        return None, None

    tags = [t.strip() for t in (lead.get("service_tags") or "").split(",") if t.strip()]

    service_type = lead.get("service_type", "")
    service_tier = lead.get("service_tier", "")
    if service_type:
        tags.append(service_type)

    contacts = []
    contact_name = f"{lead['first_name']} {lead['last_name']}"
    if lead.get("email") or lead.get("phone"):
        contact = {"name": contact_name, "isContact": True}
        if lead.get("email"):
            contact["email"] = lead["email"]
        if lead.get("phone"):
            contact["phone"] = lead["phone"]
        contacts.append(contact)

    note = f"Source: PNW Canvass | Stage: {lead['pipeline_stage']}"
    if service_type:
        note += f" | Service Plan: {service_type}"
    if tags:
        note += f" | Tags: {', '.join(tags)}"
    if lead.get("notes"):
        note += f"\n{lead['notes']}"

    payload = {
        "firstName": lead["first_name"],
        "lastName": lead["last_name"],
        "street1": lead.get("street1") or "",
        "city": lead.get("city") or "",
        "countryId": 249,
        "stateId": 47,
        "zipCode": lead.get("zip") or "",
        "note": note,
        "isLead": True,
        "contacts": contacts,
        "organizationId": lead.get("organization_id") or 1,
    }

    if lead.get("lat") and lead.get("lon"):
        payload["addressGpsLat"] = lead["lat"]
        payload["addressGpsLon"] = lead["lon"]

    try:
        resp = requests.post(
            f"{base}/clients",
            json=payload,
            headers={"x-auth-token": token},
            timeout=10,
            verify=True,
        )
        resp.raise_for_status()
        data = resp.json()
        client_id = data.get("id")
        return client_id, None
    except requests.RequestException as e:
        return None, str(e)


def update_client_in_uisp(uisp_client_id, lead, designation=None):
    """Update an existing UISP client record with current lead/visit info."""
    base = current_app.config["UISP_BASE_URL"].rstrip("/")
    token = current_app.config["UISP_API_TOKEN"]
    if not token or not uisp_client_id:
        return None

    service_type = lead.get("service_type", "")
    service_tier = lead.get("service_tier", "")

    note = f"Source: PNW Canvass | Stage: {lead['pipeline_stage']}"
    if designation:
        # Convert key to readable label
        desig_label = designation.replace("_", " ").title()
        note += f" | Designation: {desig_label}"
    if service_type:
        service_label = service_type.capitalize()
        if service_tier and service_tier != "wireless":
            service_label += f" - {service_tier}"
        note += f" | Service: {service_label}"
    if lead.get("notes"):
        note += f"\n{lead['notes']}"

    payload = {"note": note}

    try:
        resp = requests.patch(
            f"{base}/clients/{uisp_client_id}",
            json=payload,
            headers={"x-auth-token": token},
            timeout=10,
            verify=True,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None
