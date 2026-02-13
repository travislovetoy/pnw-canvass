/* ── Lead Form (inline side panel) ── */

document.getElementById('btn-save-lead').onclick = async () => {
    const first = document.getElementById('lead-first').value.trim();
    const last = document.getElementById('lead-last').value.trim();
    if (!first || !last) {
        alert('First and Last name are required.');
        return;
    }

    const visitId = document.getElementById('lead-visit-id').value;
    const leadId = document.getElementById('lead-lead-id') ? document.getElementById('lead-lead-id').value : '';
    const planSel = document.getElementById('lead-service-plan');
    const servicePlanId = planSel.value || '';
    const servicePlanName = planSel.selectedOptions[0] ? planSel.selectedOptions[0].textContent : '';

    const data = {
        first_name: first,
        last_name: last,
        street1: document.getElementById('lead-street').value,
        city: document.getElementById('lead-city').value,
        state: document.getElementById('lead-state').value || 'WA',
        zip: document.getElementById('lead-zip').value,
        lat: parseFloat(document.getElementById('lead-lat').value),
        lon: parseFloat(document.getElementById('lead-lon').value),
        phone: document.getElementById('lead-phone').value,
        email: document.getElementById('lead-email').value,
        service_type: servicePlanName,
        service_tier: servicePlanId,
        service_tags: servicePlanName || '',
        notes: document.getElementById('lead-notes').value,
        organization_id: 1,
    };

    const statusEl = document.getElementById('lead-save-status');
    statusEl.textContent = 'Saving...';
    statusEl.className = 'small text-center mt-1 text-muted';

    try {
        let r;
        if (leadId) {
            // Update existing lead
            r = await fetch(`/api/leads/${leadId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        } else {
            // Create new lead
            r = await fetch('/api/leads', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        }
        const lead = await r.json();

        // Link visit to lead (only needed for new leads)
        if (!leadId && visitId) {
            await fetch(`/api/visits/${visitId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lead_id: lead.id }),
            });
        }

        if (lead.uisp_synced === 1) {
            statusEl.textContent = 'Saved & synced to UISP!';
            statusEl.className = 'small text-center mt-1 text-success';
        } else if (lead.uisp_synced === -1) {
            statusEl.textContent = 'Saved, but UISP sync failed.';
            statusEl.className = 'small text-center mt-1 text-warning';
        } else {
            statusEl.textContent = leadId ? 'Lead updated!' : 'Lead saved!';
            statusEl.className = 'small text-center mt-1 text-success';
        }
    } catch (e) {
        statusEl.textContent = 'Error saving lead.';
        statusEl.className = 'small text-center mt-1 text-danger';
    }
};
