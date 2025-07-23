// ========== CARDS - ARRASTAR E SOLTAR ==========

function criarCardAtividadeDOM(titulo, atividadeId = null) {
    const card = document.createElement('div');
    card.className = 'drag-card';
    card.setAttribute('ondrop', 'soltar(event)');
    card.setAttribute('ondragover', 'permitirSoltar(event)');
    if (atividadeId) card.setAttribute('data-id', atividadeId);

    if (titulo !== 'Expediente Administrativo') {
        const btnClose = document.createElement('span');
        btnClose.className = 'close';
        btnClose.innerHTML = '&times;';
        btnClose.onclick = () => {
            const servidores = card.querySelectorAll('.drag-servidor');
            const expCard = document.getElementById('expediente').querySelector('.servidores-list');
            servidores.forEach(s => expCard.appendChild(s));
            card.remove();
        };
        card.appendChild(btnClose);
    }

    const h = document.createElement('h6');
    h.innerText = titulo;
    card.appendChild(h);

    const list = document.createElement('div');
    list.className = 'servidores-list';
    card.appendChild(list);

    if (titulo !== 'Expediente Administrativo') {
        const selectDiv = document.createElement('div');
        selectDiv.className = "veiculo-div mt-auto";
        selectDiv.style.width = "100%";

        const selectLabel = document.createElement('label');
        selectLabel.innerText = "Veículo:";
        selectLabel.style.fontWeight = "bold";
        selectLabel.style.display = "block";
        selectLabel.className = "mb-1";

        const select = document.createElement('select');
        select.className = "form-select form-select-sm";
        select.style.width = "100%";
        select.setAttribute('data-select-veiculo', '');

        // choicesVeiculos precisa ser global ou importado
        if (window.choicesVeiculos) {
            window.choicesVeiculos.getValue().forEach(v => {
                const opt = document.createElement('option');
                opt.value = v.value;
                opt.text = v.label;
                select.appendChild(opt);
            });
        }

        selectDiv.appendChild(selectLabel);
        selectDiv.appendChild(select);
        card.appendChild(selectDiv);
    }
    return card;
}

function criarServidorDOM(nome, valor, noExpediente = false) {
    const div = document.createElement('div');
    div.className = 'drag-servidor';
    div.setAttribute('draggable', 'true');
    div.setAttribute('data-id', valor);
    div.innerText = nome;
    div.ondragstart = arrastar;

    // Adiciona botão X se não for expediente
    if (!noExpediente) {
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-danger ms-2';
        btn.innerHTML = '<i class="bi bi-x"></i>';
        btn.onclick = function(e) {
            document.getElementById("expediente").querySelector('.servidores-list').appendChild(div);
            btn.remove();
            e.stopPropagation();
        };
        div.appendChild(btn);
    }
    return div;
}

// DRAG AND DROP
let draggedItem = null;
window.arrastar = function(ev) {
    draggedItem = ev.target;
}
window.permitirSoltar = function(ev) {
    ev.preventDefault();
    ev.currentTarget.classList.add("drag-over");
}
window.soltar = function(ev) {
    ev.preventDefault();
    if (draggedItem && ev.currentTarget !== draggedItem.parentNode) {
        if (ev.currentTarget.parentNode && ev.currentTarget.parentNode.id !== "expediente") {
            if (!draggedItem.querySelector('.btn-sm')) {
                const btn = document.createElement('button');
                btn.className = 'btn btn-sm btn-danger ms-2';
                btn.innerHTML = '<i class="bi bi-x"></i>';
                btn.onclick = function(e) {
                    document.getElementById("expediente").querySelector('.servidores-list').appendChild(draggedItem);
                    btn.remove();
                    e.stopPropagation();
                };
                draggedItem.appendChild(btn);
            }
        } else {
            draggedItem.querySelector('.btn-sm')?.remove();
        }
        ev.currentTarget.querySelector('.servidores-list').appendChild(draggedItem);
    }
    ev.currentTarget.classList.remove("drag-over");
}

// Botão criar card (isso depende do DOM já carregado!)
document.addEventListener("DOMContentLoaded", function() {
    const btnCriarAtividade = document.getElementById('btnCriarAtividade');
    if (btnCriarAtividade) {
        btnCriarAtividade.onclick = function() {
            const atividadeSel = document.getElementById('atividadeSelect');
            const nomeAtividade = atividadeSel.options[atividadeSel.selectedIndex]?.text;
            const atividadeId = atividadeSel.value;
            if (!nomeAtividade) return alert('Selecione a atividade!');
            const existe = Array.from(document.querySelectorAll('.drag-card h6')).some(el => el.innerText == nomeAtividade);
            if (existe) return alert('Já existe um card para esta atividade.');
            document.getElementById('cardsContainer').appendChild(criarCardAtividadeDOM(nomeAtividade, atividadeId));
        };
    }
});