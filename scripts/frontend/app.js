// Aplicação Vue 3 — Despesas Pessoais
const { createApp, ref, computed, onMounted, watch, nextTick } = Vue;

createApp({
    setup() {
        const API_BASE = window.location.port === '8000' ? '' : 'http://localhost:8000';

        // --- Estado global ---
        const isLoading     = ref(false);
        const apiOnline     = ref(false);
        const searchQuery   = ref('');

        // --- Filtros de período ---
        const now           = new Date();
        const selectedYear  = ref(now.getFullYear());
        const selectedMonth = ref(now.getMonth() + 1);

        const availableYears = [2024, 2025, 2026];
        const monthsList = [
            { id: 1,  name: 'Janeiro'   }, { id: 2,  name: 'Fevereiro' }, { id: 3,  name: 'Março'     },
            { id: 4,  name: 'Abril'     }, { id: 5,  name: 'Maio'      }, { id: 6,  name: 'Junho'     },
            { id: 7,  name: 'Julho'     }, { id: 8,  name: 'Agosto'    }, { id: 9,  name: 'Setembro'  },
            { id: 10, name: 'Outubro'   }, { id: 11, name: 'Novembro'  }, { id: 12, name: 'Dezembro'  }
        ];

        // --- Dados da API ---
        const despesas       = ref([]);           
        const despesasAno    = ref([]);           
        const categorias     = ref([]);           
        const gastosMensais  = ref([]);           
        const metas          = ref([]);           
        const rendas         = ref([]);           // GET /rendas?ano=&mes=

        const formasPagamento = ref([
            { id: 1, nome: 'Débito/Pix' },
            { id: 2, nome: 'Crédito'    }
        ]);

        // --- Modais e notificações ---
        const isModalOpen           = ref(false);
        const isRendaModalOpen      = ref(false);
        const isRecorrenteModalOpen = ref(false);
        const isSubmitting          = ref(false);
        const toast                 = ref({ show: false, message: '', type: 'success' });
        const deleteConfirm         = ref({ show: false, id: null, desc: '' });

        // --- Formulários ---
        const newDespesa = ref({
            data: now.toISOString().split('T')[0], valor: '', descricao: '',
            categoria_id: 1, forma_pagamento_id: 1
        });
        const newRenda = ref({
            data: now.toISOString().split('T')[0], valor: '', descricao: ''
        });
        const newRecorrente = ref({
            nome: '', valor_estimado: '', dia_vencimento: 1, categoria_id: 1
        });

        let areaChartInstance  = null;
        let donutChartInstance = null;

        // ─── Helpers ──────────────────────────────────────────────
        const showToast = (message, type = 'success') => {
            toast.value = { show: true, message, type };
            setTimeout(() => { toast.value.show = false; }, 4000);
        };

        const formatCurrency = (val) => {
            if (val == null || isNaN(val)) return 'R$ 0,00';
            return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
        };

        const formatDate = (dateStr) => {
            if (!dateStr) return '';
            const [y, m, d] = dateStr.split('-');
            return `${d}/${m}/${y}`;
        };

        // ─── Maps auxiliares ──────────────────────────────────────
        const categoriaMap = computed(() => {
            const map = {};
            categorias.value.forEach(c => { map[c.id] = c.nome; });
            return map;
        });

        const formaPagamentoMap = computed(() => {
            const map = {};
            formasPagamento.value.forEach(f => { map[f.id] = f.nome; });
            return map;
        });

        // ─── Computed: métricas do mês ────────────────────────────
        const filteredDespesas = computed(() => {
            if (!searchQuery.value.trim()) return despesas.value;
            const q = searchQuery.value.toLowerCase();
            return despesas.value.filter(d => {
                return (d.descricao || '').toLowerCase().includes(q)
                    || (categoriaMap.value[d.categoria_id] || '').toLowerCase().includes(q)
                    || (formaPagamentoMap.value[d.forma_pagamento_id] || '').toLowerCase().includes(q);
            });
        });

        const isInvestimento = (d) => (categoriaMap.value[d.categoria_id] || '').toLowerCase().includes('investimento');

        const totalRenda = computed(() => rendas.value.reduce((s, r) => s + r.valor, 0));
        
        const totalGastosGeral = computed(() => despesas.value.filter(d => !isInvestimento(d)).reduce((s, d) => s + d.valor, 0));
        
        const totalInvestimentos = computed(() => despesas.value.filter(d => isInvestimento(d)).reduce((s, d) => s + d.valor, 0));
        
        const totalInvestimentosAno = computed(() => despesasAno.value.filter(d => isInvestimento(d)).reduce((s, d) => s + d.valor, 0));

        const mediaDiaria = computed(() => {
            if (!despesas.value.length) return 0;
            const daysInMonth = new Date(selectedYear.value, selectedMonth.value, 0).getDate();
            return totalGastosGeral.value / daysInMonth;
        });

        // Agrupamento e proporção baseada na Renda (30% Necessidade, 30% Lazer, 40% Investimento)
        const gastosPorCategoria = computed(() => {
            const groups = {};
            const rendaAtual = totalRenda.value || 0;

            categorias.value.forEach(cat => {
                const nomeLower = cat.nome.toLowerCase();
                let metaCalculada = 0;

                if (nomeLower.includes('necessidade')) {
                    metaCalculada = rendaAtual * 0.30;
                } else if (nomeLower.includes('lazer') || nomeLower.includes('vontade')) {
                    metaCalculada = rendaAtual * 0.30;
                } else if (nomeLower.includes('investimento')) {
                    metaCalculada = rendaAtual * 0.40;
                } else {
                    metaCalculada = cat.meta_gastos || 0; 
                }

                groups[cat.nome] = {
                    id: cat.id, nome: cat.nome, total: 0,
                    meta: metaCalculada
                };
            });
            despesas.value.forEach(d => {
                const nome = categoriaMap.value[d.categoria_id] || 'Outros';
                if (!groups[nome]) groups[nome] = { id: d.categoria_id, nome, total: 0, meta: 0 };
                groups[nome].total += d.valor;
            });
            return Object.values(groups);
        });

        // ─── Chamadas à API ───────────────────────────────────────
        const checkApiHealth = async () => {
            try { apiOnline.value = (await fetch(`${API_BASE}/`)).ok; } catch { apiOnline.value = false; }
        };

        const fetchCategorias = async () => {
            try {
                const res = await fetch(`${API_BASE}/categorias/`);
                if (res.ok) categorias.value = await res.json();
            } catch (err) { console.error('categorias:', err); }
        };

        const fetchRendas = async () => {
            try {
                const res = await fetch(`${API_BASE}/renda?ano=${selectedYear.value}&mes=${selectedMonth.value}`);
                if (res.ok) rendas.value = await res.json();
            } catch (err) { console.error('rendas:', err); }
        };

        const fetchDespesas = async () => {
            isLoading.value = true;
            try {
                const res = await fetch(`${API_BASE}/despesas?ano=${selectedYear.value}&mes=${selectedMonth.value}`);
                if (res.ok) {
                    despesas.value = await res.json();
                    apiOnline.value = true;
                }
            } catch {
                apiOnline.value = false;
            } finally {
                isLoading.value = false;
                nextTick(renderOrUpdateCharts);
            }
        };

        const fetchDespesasAno = async () => {
            try {
                const res = await fetch(`${API_BASE}/despesas?ano=${selectedYear.value}`);
                if (res.ok) despesasAno.value = await res.json();
            } catch (err) { console.error('despesas ano:', err); }
        };

        const fetchGastosMensais = async () => {
            try {
                const res = await fetch(`${API_BASE}/gastos-mensais/`);
                if (res.ok) gastosMensais.value = await res.json();
            } catch (err) { console.error('gastos-mensais:', err); }
        };

        const fetchMetas = async () => {
            try {
                const res = await fetch(`${API_BASE}/metas/`);
                if (res.ok) metas.value = await res.json();
            } catch (err) { console.error('metas:', err); }
        };

        // ─── Operações de escrita ─────────────────────────────────
        const openCreateModal = () => {
            newDespesa.value = {
                data: new Date().toISOString().split('T')[0], valor: '', descricao: '',
                categoria_id: categorias.value[0]?.id || 1, forma_pagamento_id: 1
            };
            isModalOpen.value = true;
        };

        const submitDespesa = async () => {
            if (!newDespesa.value.valor || newDespesa.value.valor <= 0) return showToast('Informe um valor válido', 'error');
            isSubmitting.value = true;
            try {
                const payload = {
                    data: newDespesa.value.data,
                    valor: parseFloat(newDespesa.value.valor),
                    descricao: newDespesa.value.descricao || 'Sem descrição',
                    forma_pagamento_id: parseInt(newDespesa.value.forma_pagamento_id),
                    categoria_id: parseInt(newDespesa.value.categoria_id)
                };
                const res = await fetch(`${API_BASE}/despesas`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                if (res.ok) {
                    showToast('Despesa cadastrada!');
                    isModalOpen.value = false;
                    await fetchDespesas();
                    await fetchDespesasAno();
                } else { showToast('Erro ao salvar', 'error'); }
            } catch { showToast('Erro de comunicação', 'error'); } finally { isSubmitting.value = false; }
        };

        const submitRenda = async () => {
            if (!newRenda.value.valor || newRenda.value.valor <= 0) return showToast('Informe um valor válido', 'error');
            isSubmitting.value = true;
            try {
                const payload = {
                    data: newRenda.value.data,
                    valor: parseFloat(newRenda.value.valor),
                    descricao: newRenda.value.descricao || 'Renda'
                };
                const res = await fetch(`${API_BASE}/renda`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                if (res.ok) {
                    showToast('Renda cadastrada!');
                    isRendaModalOpen.value = false;
                    await fetchRendas();
                } else { showToast('Erro ao salvar', 'error'); }
            } catch { showToast('Erro de comunicação', 'error'); } finally { isSubmitting.value = false; }
        };

        const submitRecorrente = async () => {
            if (!newRecorrente.value.valor_estimado || newRecorrente.value.valor_estimado <= 0) return showToast('Valor inválido', 'error');
            isSubmitting.value = true;
            try {
                const payload = {
                    nome: newRecorrente.value.nome,
                    valor_estimado: parseFloat(newRecorrente.value.valor_estimado),
                    dia_vencimento: parseInt(newRecorrente.value.dia_vencimento),
                    categoria_id: parseInt(newRecorrente.value.categoria_id)
                };
                const res = await fetch(`${API_BASE}/gastos-mensais`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                if (res.ok) {
                    showToast('Recorrência cadastrada!');
                    isRecorrenteModalOpen.value = false;
                    await fetchGastosMensais();
                } else { showToast('Erro ao salvar', 'error'); }
            } catch { showToast('Erro de comunicação', 'error'); } finally { isSubmitting.value = false; }
        };

        const confirmDelete = (despesa) => {
            deleteConfirm.value = { show: true, id: despesa.id, desc: `${despesa.descricao || 'Despesa'} (${formatCurrency(despesa.valor)})` };
        };

        const executeDelete = async () => {
            if (!deleteConfirm.value.id) return;
            try {
                const res = await fetch(`${API_BASE}/despesas/${deleteConfirm.value.id}`, { method: 'DELETE' });
                if (res.ok) {
                    showToast('Despesa excluída!');
                    deleteConfirm.value.show = false;
                    await fetchDespesas();
                    await fetchDespesasAno();
                } else { showToast('Erro ao excluir', 'error'); }
            } catch { showToast('Erro de comunicação', 'error'); }
        };

        // ─── Gráficos ApexCharts ──────────────────────────────────
        const chartDefaults = {
            chart: { background: 'transparent', foreColor: '#64748b' },
            tooltip: { theme: 'dark' },
            grid: { borderColor: 'rgba(255,255,255,0.05)', strokeDashArray: 4 }
        };

        const renderOrUpdateCharts = () => {
            const cats = gastosPorCategoria.value.filter(c => c.total > 0);
            const donutEl = document.querySelector('#donutChart');
            if (donutEl) {
                if (donutChartInstance) { donutChartInstance.destroy(); donutChartInstance = null; }
                donutChartInstance = new ApexCharts(donutEl, {
                    ...chartDefaults,
                    series: cats.length ? cats.map(c => +c.total.toFixed(2)) : [1],
                    labels: cats.length ? cats.map(c => c.nome) : ['Sem dados'],
                    chart: { ...chartDefaults.chart, type: 'donut', height: 290 },
                    colors: ['#f59e0b', '#3b82f6', '#10b981', '#ec4899', '#8b5cf6'],
                    stroke: { colors: ['#050508'], width: 3 },
                    legend: { position: 'bottom', labels: { colors: '#64748b' } },
                    dataLabels: { enabled: cats.length > 0 },
                    tooltip: { theme: 'dark', y: { formatter: v => formatCurrency(v) } },
                    plotOptions: { pie: { donut: { size: '65%' } } }
                });
                donutChartInstance.render();
            }

            const daily = {};
            despesas.value.forEach(d => {
                const day = d.data.split('-')[2];
                daily[day] = (daily[day] || 0) + d.valor;
            });
            const days   = Object.keys(daily).sort();
            const values = days.map(d => +daily[d].toFixed(2));

            const areaEl = document.querySelector('#areaChart');
            if (areaEl) {
                if (areaChartInstance) { areaChartInstance.destroy(); areaChartInstance = null; }
                areaChartInstance = new ApexCharts(areaEl, {
                    ...chartDefaults,
                    series: [{ name: 'Gastos', data: values.length ? values : [0] }],
                    chart: { ...chartDefaults.chart, type: 'area', height: 250, toolbar: { show: false } },
                    colors: ['#3b82f6'],
                    fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.35, opacityTo: 0.02, stops: [0, 100] } },
                    stroke: { curve: 'smooth', width: 2 },
                    xaxis: { categories: days.length ? days.map(d => `${d}`) : ['—'], labels: { style: { colors: '#475569', fontSize: '11px' } }, axisBorder: { show: false }, axisTicks: { show: false } },
                    yaxis: { labels: { formatter: v => `R$${v.toFixed(0)}`, style: { colors: '#475569', fontSize: '11px' } } },
                    tooltip: { theme: 'dark', y: { formatter: v => formatCurrency(v) } },
                    grid: { borderColor: 'rgba(255,255,255,0.04)', strokeDashArray: 3 }
                });
                areaChartInstance.render();
            }
        };

        watch(selectedYear, async () => { await Promise.all([fetchDespesas(), fetchDespesasAno(), fetchRendas()]); });
        watch(selectedMonth, () => { fetchDespesas(); fetchRendas(); });
        const onFilterChange = () => { };

        onMounted(async () => {
            await checkApiHealth();
            await fetchCategorias();
            await Promise.all([
                fetchDespesas(), fetchDespesasAno(), fetchRendas(), fetchGastosMensais(), fetchMetas()
            ]);
        });

        return {
            isLoading, apiOnline, searchQuery, selectedYear, selectedMonth, availableYears, monthsList,
            despesas, categorias, gastosMensais, metas, formasPagamento, rendas,
            categoriaMap, formaPagamentoMap,
            filteredDespesas, totalRenda, totalGastosGeral, totalInvestimentos, totalInvestimentosAno, mediaDiaria, gastosPorCategoria,
            isModalOpen, isRendaModalOpen, isRecorrenteModalOpen, isSubmitting, 
            newDespesa, newRenda, newRecorrente, toast, deleteConfirm,
            formatCurrency, formatDate,
            openCreateModal, submitDespesa, submitRenda, submitRecorrente, confirmDelete, executeDelete, onFilterChange
        };
    }
}).mount('#app');