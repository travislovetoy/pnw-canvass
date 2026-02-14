const stages = ['new_lead', 'contacted', 'quoted', 'won', 'lost'];
const stageLabels = {new_lead:'New Lead',contacted:'Contacted',quoted:'Quoted',won:'Won',lost:'Lost'};

async function loadPipeline() {
    const r = await fetch('/api/leads');
    const leads = await r.json();

    stages.forEach(s => {
        document.getElementById('stage-' + s).innerHTML = '';
        document.getElementById('count-' + s).textContent = '0';
    });

    const counts = {};
    stages.forEach(s => counts[s] = 0);

    leads.forEach(lead => {
        const col = document.getElementById('stage-' + lead.pipeline_stage);
        if (!col) return;
        counts[lead.pipeline_stage]++;

        const card = document.createElement('div');
        card.className = 'card lead-card';
        card.draggable = true;
        card.dataset.leadId = lead.id;

        let syncBadge = '';
        if (lead.uisp_synced === 1) syncBadge = '<span class="badge bg-success">Synced</span>';
        else if (lead.uisp_synced === -1) syncBadge = '<span class="badge bg-danger">Failed</span>';

        card.innerHTML = `<div class="card-body p-2">
            <div class="d-flex justify-content-between">
                <a href="/leads/${lead.id}" class="text-decoration-none fw-bold">${lead.first_name} ${lead.last_name}</a>
                ${syncBadge}
            </div>
            <small class="text-muted">${lead.street1 || ''} ${lead.city || ''}</small>
        </div>`;

        card.addEventListener('dragstart', e => {
            e.dataTransfer.setData('text/plain', lead.id);
            card.style.opacity = '0.5';
        });
        card.addEventListener('dragend', () => { card.style.opacity = '1'; });

        col.appendChild(card);
    });

    stages.forEach(s => {
        document.getElementById('count-' + s).textContent = counts[s];
    });
}

// Drop targets
stages.forEach(stage => {
    const col = document.getElementById('stage-' + stage);
    col.addEventListener('dragover', e => {
        e.preventDefault();
        col.classList.add('drag-over');
    });
    col.addEventListener('dragleave', () => col.classList.remove('drag-over'));
    col.addEventListener('drop', async e => {
        e.preventDefault();
        col.classList.remove('drag-over');
        const leadId = e.dataTransfer.getData('text/plain');
        await fetch(`/api/leads/${leadId}/stage`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({pipeline_stage: stage}),
        });
        loadPipeline();
    });
});

loadPipeline();
