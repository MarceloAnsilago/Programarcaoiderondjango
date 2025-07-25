// ========== CARDS - ARRASTAR E SOLTAR ==========

function criarCardAtividadeDOM(titulo, atividadeId = null) {
    const card = document.createElement('div');
    card.className = 'drag-card';
    card.setAttribute('ondrop', 'soltar(event)');
    card.setAttribute('ondragover', 'permitirSoltar(event)');
    card.setAttribute('data-id', atividadeId || '');
    card.setAttribute('data-titulo', titulo);

    if (titulo !== 'Expediente Administrativo') {
        const btnClose = document.createElement('span');
        btnClose.className = 'close';
        btnClose.innerHTML = '&times;';
        btnClose.onclick = () => {
            const servidores = card.querySelectorAll('.drag-servidor');
            const expCard = document.getElementById('expediente').querySelector('.servidores-list');
            servidores.forEach(s => expCard.appendChild(s));
            card.remove();
            atualizarIndicesCards();
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

    if (!noExpediente) {
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm btn-danger ms-2';
        btn.innerHTML = '<i class="bi bi-x"></i>';
        btn.onclick = function (e) {
            document.getElementById("expediente").querySelector('.servidores-list').appendChild(div);
            btn.remove();
            e.stopPropagation();
        };
        div.appendChild(btn);
    }

    return div;
}

// ========== DRAG SERVIDOR ==========
let draggedItem = null;
window.arrastar = function (ev) {
    draggedItem = ev.target;
}
window.permitirSoltar = function (ev) {
    ev.preventDefault();
    ev.currentTarget.classList.add("drag-over");
}
window.soltar = function (ev) {
    ev.preventDefault();
    if (draggedItem && ev.currentTarget !== draggedItem.parentNode) {
        if (ev.currentTarget.parentNode && ev.currentTarget.parentNode.id !== "expediente") {
            if (!draggedItem.querySelector('.btn-sm')) {
                const btn = document.createElement('button');
                btn.className = 'btn btn-sm btn-danger ms-2';
                btn.innerHTML = '<i class="bi bi-x"></i>';
                btn.onclick = function (e) {
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

// ========== DRAG DOS CARDS ==========
let draggedCard = null;

function tornarCardArrastavel(card) {
    if (card.id === 'expediente') return;

    card.setAttribute('draggable', 'true');

    card.addEventListener('dragstart', e => {
    console.log('🔹 dragstart no card:', card);
    draggedCard = card;
    e.dataTransfer.setData('text/plain', '');
    card.classList.add('dragging-card');
    });
    card.addEventListener('dragend', () => {
        draggedCard = null;
        document.querySelectorAll('.drag-card').forEach(c => c.classList.remove('drag-over-card', 'dragging-card'));
    });

    card.addEventListener('dragover', e => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        card.classList.add('drag-over-card');
    });

    card.addEventListener('dragleave', () => {
        card.classList.remove('drag-over-card');
    });

    card.addEventListener('drop', e => {
        e.preventDefault();
        card.classList.remove('drag-over-card');

        if (draggedCard && draggedCard !== card) {
            const container = document.getElementById('cardsContainer');
            const allCards = [...container.querySelectorAll('.drag-card')].filter(c => c.id !== 'expediente');

            const targetIndex = allCards.indexOf(card);
            const draggedIndex = allCards.indexOf(draggedCard);

            if (draggedIndex < targetIndex) {
                container.insertBefore(draggedCard, card.nextSibling);
            } else {
                container.insertBefore(draggedCard, card);
            }

            atualizarIndicesCards();
        }
    });
}
document.addEventListener("DOMContentLoaded", function () {
    const btnCriarAtividade = document.getElementById('btnCriarAtividade');

    if (btnCriarAtividade) {
        btnCriarAtividade.onclick = function () {
            const atividadeSel = document.getElementById('atividadeSelect');
            const nomeAtividade = atividadeSel.options[atividadeSel.selectedIndex]?.text;
            const atividadeId = atividadeSel.value;

            if (!nomeAtividade) {
                alert('Selecione a atividade!');
                return;
            }

            const existe = Array.from(document.querySelectorAll('.drag-card h6'))
                .some(el => el.innerText.trim().toLowerCase() === nomeAtividade.toLowerCase());

            if (existe) {
                alert('Já existe um card para esta atividade.');
                return;
            }

            const cardsContainer = document.getElementById('cardsContainer');
            const novoCard = criarCardAtividadeDOM(nomeAtividade, atividadeId);

            // Inserção após expediente
            const dragCards = [...cardsContainer.children].filter(el =>
                el.classList?.contains('drag-card')
            );
            const expedienteCard = dragCards.find(el => {
                const h = el.querySelector('h6');
                return h?.textContent?.trim().toLowerCase() === 'expediente administrativo';
            });

            if (expedienteCard) {
                const index = dragCards.indexOf(expedienteCard);
                const insertBeforeEl = dragCards[index + 1] || null;
                cardsContainer.insertBefore(novoCard, insertBeforeEl);
            } else {
                cardsContainer.appendChild(novoCard);
            }

            tornarCardArrastavel(novoCard); // ← torna novo card arrastável

            // Destaque temporário
            novoCard.style.transition = 'background 0.6s ease';
            novoCard.style.background = '#d1ffd6';
            setTimeout(() => {
                novoCard.style.background = '';
            }, 1000);

            novoCard.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            atualizarIndicesCards();
        };
    }

    // Torna cards existentes arrastáveis (exceto expediente)
    document.querySelectorAll('.drag-card').forEach(card => tornarCardArrastavel(card));
});

// ========== ATUALIZAR ÍNDICES ==========
