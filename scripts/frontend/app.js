// Aplicação Vue 3 - Despesas Pessoais
const { createApp, ref, computed, onMounted, watch, nextTick } = Vue;

createApp({
    setup() {
        // --- Configuração da API ---
        // Se rodar na porta 8000 (FastAPI), usa URL relativa. Se rodar em porta diferente (ex: Live Server), usa localhost:8000.
        const API_BASE = window.location.port === '8000' ? '' : 'http://localhost:8000';

        // --- Estado Principal ---
        const activeTab = ref('dashboard'); // 'dashboard' | 'lancamentos' | 'metas' | 'config'
        const isLoading = ref(false);
        const apiOnline = ref(false);

        // --- Filtros ---
        const currentDate = new Date();
        const selectedYear = ref(currentDate.getFullYear()); // 2026
        const selectedMonth = ref(currentDate.getMonth() + 1); // 1 a 12
        const searchQuery = ref('');

        const availableYears = [2024, 2025, 2026];
        const monthsList = [
            { id: 1, name: 'Janeiro' },
            { id: 2, name: 'Fevereiro' },
            { id: 3, name: 'Março' },
            { id: 4, name: 'Abril' },
            { id: 5, name: 'Maio' },
            { id: 6, name: 'Junho' },
            { id: 7, name: 'Julho' },
            { id: 8, name: 'Agosto' },
            { id: 9, name: 'Setembro' },
            { id: 10, name: 'Outubro' },
            { id: 11, name: 'Novembro' },
            { id: 12, name: 'Dezembro' }
        ];

        // --- Dados Carregados ---
        const despesas = ref([]);
        const categorias = ref([]);
        const formasPagamento = ref([
            { id: 1, nome: 'Débito/Pix' },
            { id: 2, nome: 'Crédito' }
        ]);

        // --- Modais e Notificações ---
        const isModalOpen = ref(false);
        const isSubmitting = ref(false);
        const toast = ref({ show: false, message: '', type: 'success' });
        const deleteConfirm = ref({ show: false, id: null, desc: '' });

        // --- Formulário de Nova Despesa ---
        const newDespesa = ref({
            data: new Date().toISOString().split('T')[0],
            valor: '',
            descricao: '',
            categoria_id: 1,
            forma_pagamento_id: 1
        });

        // --- Instâncias dos Gráficos ApexCharts ---
        let areaChartInstance = null;
        let donutChartInstance = null;

        // --- Notificações Toast ---
        const showToast = (message, type = 'success') => {
            toast.value = { show: true, message, type };
            setTimeout(() => {
                toast.value.show = false;
            }, 4000);
        };

        // --- Mapeamento Auxiliar ---
        const categoriaMap = computed(() => {
            const map = {};
            categorias.value.forEach(c => {
                map[c.id] = c.nome;
            });
            return map;
        });

        const formaPagamentoMap = computed(() => {
            const map = {};
            formasPagamento.value.forEach(f => {
                map[f.id] = f.nome;
            });
            return map;
        });

        // --- Formatação de Moeda ---
        const formatCurrency = (val) => {
            if (val === null || val === undefined || isNaN(val)) return 'R$ 0,00';
            return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
        };

        // --- Formatação de Data ---
        const formatDate = (dateStr) => {
            if (!dateStr) return '';
            const parts = dateStr.split('-');
            if (parts.length === 3) {
                return `${parts[2]}/${parts[1]}/${parts[0]}`;
            }
            return dateStr;
        };

        // --- Chamadas à API ---
        const checkApiHealth = async () => {
            try {
                const res = await fetch(`${API_BASE}/`);
                if (res.ok) {
                    apiOnline.value = true;
                } else {
                    apiOnline.value = false;
                }
            } catch (err) {
                apiOnline.value = false;
            }
        };

        const fetchCategorias = async () => {
            try {
                const res = await fetch(`${API_BASE}/despesas/categorias`);
                if (res.ok) {
                    categorias.value = await res.json();
                }
            } catch (err) {
                console.error('Erro ao buscar categorias:', err);
            }
        };

        const fetchDespesas = async () => {
            isLoading.value = true;
            try {
                let url = `${API_BASE}/despesas?ano=${selectedYear.value}`;
                if (selectedMonth.value) {
                    url += `&mes=${selectedMonth.value}`;
                }
                const res = await fetch(url);
                if (res.ok) {
                    despesas.value = await res.json();
                    apiOnline.value = true;
                } else {
                    showToast('Erro ao carregar despesas', 'error');
                }
            } catch (err) {
                apiOnline.value = false;
                showToast('Falha na conexão com o backend FastAPI', 'error');
            } finally {
                isLoading.value = false;
                nextTick(() => {
                    renderOrUpdateCharts();
                });
            }
        };

        // --- Lista Filtrada por Busca ---
        const filteredDespesas = computed(() => {
            if (!searchQuery.value.trim()) {
                return despesas.value;
            }
            const q = searchQuery.value.toLowerCase();
            return despesas.value.filter(d => {
                const desc = (d.descricao || '').toLowerCase();
                const cat = (categoriaMap.value[d.categoria_id] || '').toLowerCase();
                const pag = (formaPagamentoMap.value[d.forma_pagamento_id] || '').toLowerCase();
                return desc.includes(q) || cat.includes(q) || pag.includes(q);
            });
        });

        // --- Métricas Calculadas (KPIs) ---
        const totalGastosGeral = computed(() => {
            return despesas.value
                .filter(d => {
                    const catName = (categoriaMap.value[d.categoria_id] || '').toLowerCase();
                    return !catName.includes('investimento');
                })
                .reduce((acc, curr) => acc + curr.valor, 0);
        });

        const totalInvestimentos = computed(() => {
            return despesas.value
                .filter(d => {
                    const catName = (categoriaMap.value[d.categoria_id] || '').toLowerCase();
                    return catName.includes('investimento');
                })
                .reduce((acc, curr) => acc + curr.valor, 0);
        });

        const mediaDiaria = computed(() => {
            if (!despesas.value.length) return 0;
            const daysInMonth = new Date(selectedYear.value, selectedMonth.value, 0).getDate();
            return totalGastosGeral.value / daysInMonth;
        });

        // Agrupamento por Categoria para Gráfico e Orçamento
        const gastosPorCategoria = computed(() => {
            const groups = {};
            categorias.value.forEach(cat => {
                groups[cat.nome] = {
                    id: cat.id,
                    nome: cat.nome,
                    total: 0,
                    meta: cat.meta_gastos || (cat.nome.toLowerCase().includes('lazer') ? 1500 : 2500)
                };
            });

            despesas.value.forEach(d => {
                const catName = categoriaMap.value[d.categoria_id] || 'Outros';
                if (!groups[catName]) {
                    groups[catName] = { id: d.categoria_id, nome: catName, total: 0, meta: 1000 };
                }
                groups[catName].total += d.valor;
            });

            return Object.values(groups);
        });

        // --- Operações de Escrita (POST e DELETE) ---
        const openCreateModal = () => {
            newDespesa.value = {
                data: new Date().toISOString().split('T')[0],
                valor: '',
                descricao: '',
                categoria_id: categorias.value[0]?.id || 1,
                forma_pagamento_id: 1
            };
            isModalOpen.value = true;
        };

        const submitDespesa = async () => {
            if (!newDespesa.value.valor || newDespesa.value.valor <= 0) {
                showToast('Informe um valor válido maior que zero', 'error');
                return;
            }
            if (!newDespesa.value.data) {
                showToast('Selecione a data da despesa', 'error');
                return;
            }

            isSubmitting.value = true;
            try {
                const payload = {
                    data: newDespesa.value.data,
                    valor: parseFloat(newDespesa.value.valor),
                    descricao: newDespesa.value.descricao || 'Sem descrição',
                    forma_pagamento_id: parseInt(newDespesa.value.forma_pagamento_id),
                    categoria_id: parseInt(newDespesa.value.categoria_id)
                };

                const res = await fetch(`${API_BASE}/despesas`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    showToast('Despesa cadastrada com sucesso!');
                    isModalOpen.value = false;
                    await fetchDespesas();
                } else {
                    const errData = await res.json().catch(() => ({}));
                    showToast(errData.detail || 'Erro ao salvar despesa', 'error');
                }
            } catch (err) {
                showToast('Erro de comunicação com o servidor', 'error');
            } finally {
                isSubmitting.value = false;
            }
        };

        const confirmDelete = (despesa) => {
            deleteConfirm.value = {
                show: true,
                id: despesa.id,
                desc: `${despesa.descricao || 'Despesa'} (${formatCurrency(despesa.valor)})`
            };
        };

        const executeDelete = async () => {
            const id = deleteConfirm.value.id;
            if (!id) return;

            try {
                const res = await fetch(`${API_BASE}/despesas/${id}`, {
                    method: 'DELETE'
                });

                if (res.ok) {
                    showToast('Despesa excluída com sucesso!');
                    deleteConfirm.value.show = false;
                    await fetchDespesas();
                } else {
                    showToast('Erro ao excluir despesa', 'error');
                }
            } catch (err) {
                showToast('Erro ao conectar com o servidor', 'error');
            }
        };

        // --- Renderização dos Gráficos com ApexCharts ---
        const renderOrUpdateCharts = () => {
            if (activeTab.value !== 'dashboard') return;

            // 1. Gráfico Donut (Distribuição por Categorias)
            const donutCategories = gastosPorCategoria.value.filter(c => c.total > 0);
            const donutLabels = donutCategories.map(c => c.nome);
            const donutSeries = donutCategories.map(c => parseFloat(c.total.toFixed(2)));

            const donutEl = document.querySelector("#donutChart");
            if (donutEl) {
                const donutOptions = {
                    series: donutSeries.length ? donutSeries : [1],
                    labels: donutSeries.length ? donutLabels : ['Sem dados'],
                    chart: {
                        type: 'donut',
                        height: 320,
                        background: 'transparent',
                        foreColor: '#94a3b8'
                    },
                    colors: ['#f59e0b', '#3b82f6', '#10b981', '#ec4899', '#8b5cf6'],
                    stroke: { colors: ['#1e293b'], width: 3 },
                    legend: { position: 'bottom', labels: { colors: '#94a3b8' } },
                    dataLabels: { enabled: true },
                    tooltip: {
                        theme: 'dark',
                        y: { formatter: val => formatCurrency(val) }
                    }
                };

                if (donutChartInstance) {
                    donutChartInstance.destroy();
                }
                donutChartInstance = new ApexCharts(donutEl, donutOptions);
                donutChartInstance.render();
            }

            // 2. Gráfico de Evolução (Gastos por Dia ou Mês)
            // Agrupar gastos por dia no mês selecionado
            const dailyData = {};
            despesas.value.forEach(d => {
                const day = d.data.split('-')[2];
                dailyData[day] = (dailyData[day] || 0) + d.valor;
            });

            const daysSorted = Object.keys(dailyData).sort();
            const seriesData = daysSorted.map(d => parseFloat(dailyData[d].toFixed(2)));

            const areaEl = document.querySelector("#areaChart");
            if (areaEl) {
                const areaOptions = {
                    series: [{
                        name: 'Gastos Diários',
                        data: seriesData.length ? seriesData : [0]
                    }],
                    chart: {
                        type: 'area',
                        height: 320,
                        background: 'transparent',
                        toolbar: { show: false },
                        foreColor: '#94a3b8'
                    },
                    colors: ['#3b82f6'],
                    fill: {
                        type: 'gradient',
                        gradient: { shadeIntensity: 1, opacityFrom: 0.45, opacityTo: 0.05, stops: [20, 100] }
                    },
                    stroke: { curve: 'smooth', width: 3 },
                    xaxis: {
                        categories: daysSorted.length ? daysSorted.map(d => `Dia ${d}`) : ['Sem lançamentos'],
                        labels: { style: { colors: '#94a3b8' } }
                    },
                    yaxis: {
                        labels: {
                            formatter: val => `R$ ${val.toFixed(0)}`,
                            style: { colors: '#94a3b8' }
                        }
                    },
                    grid: { borderColor: '#334155', strokeDashArray: 4 },
                    tooltip: {
                        theme: 'dark',
                        y: { formatter: val => formatCurrency(val) }
                    }
                };

                if (areaChartInstance) {
                    areaChartInstance.destroy();
                }
                areaChartInstance = new ApexCharts(areaEl, areaOptions);
                areaChartInstance.render();
            }
        };

        // --- Observadores de Filtro ---
        watch([selectedYear, selectedMonth], () => {
            fetchDespesas();
        });

        watch(activeTab, (newTab) => {
            if (newTab === 'dashboard') {
                nextTick(() => {
                    setTimeout(renderOrUpdateCharts, 100);
                });
            }
        });

        // --- Inicialização ---
        onMounted(async () => {
            await checkApiHealth();
            await fetchCategorias();
            await fetchDespesas();
        });

        return {
            activeTab,
            isLoading,
            apiOnline,
            selectedYear,
            selectedMonth,
            searchQuery,
            availableYears,
            monthsList,
            despesas,
            categorias,
            formasPagamento,
            categoriaMap,
            formaPagamentoMap,
            filteredDespesas,
            totalGastosGeral,
            totalInvestimentos,
            mediaDiaria,
            gastosPorCategoria,
            isModalOpen,
            isSubmitting,
            newDespesa,
            toast,
            deleteConfirm,
            formatCurrency,
            formatDate,
            openCreateModal,
            submitDespesa,
            confirmDelete,
            executeDelete,
            fetchDespesas
        };
    }
}).mount('#app');
