window.loader = function () {
  return {
    loadingText: 'Analisando jogadores...',
    progress: 0,
    phrases: [
      'Analisando jogadores...',
      'Analisando grandes fortunas...',
      'Calculando medianas...',
      'Traçando médias...',
      'Finalizando análise...'
    ],
    simulateProgress() {
      setTimeout(() => {
        let interval = 2000;
        let step = 100 / (this.phrases.length - 1);
        this.progress = 0;

        this.phrases.forEach((phrase, index) => {
          setTimeout(() => {
            this.loadingText = phrase;
            this.progress = index * step;

            if (index === this.phrases.length - 1) {
              setTimeout(() => {
                window.location.href = '/dashboard'; // ou qualquer outra rota
              }, interval);
            }
          }, index * interval);
        });
      }, 300);
    }
  }
}
window.dashboard = function () {
  return {
    metrics: [],
    async fetchMetrics() {
      try {
        const res = await fetch('/metrics');
        const data = await res.json();

        this.metrics = [
          { label: 'Total de Dinheiro', value: this.formatMoney(data.total_money) },
          { label: 'Riqueza Média', value: this.formatMoney(data.average_wealth) },
          { label: 'Riqueza Mediana', value: this.formatMoney(data.median_wealth) },
          { label: 'Jogadores Analisados', value: data.total_players },
          { label: 'Falidos (<100k)', value: data.bankrupt_players },
          { label: 'Pobres (<500k)', value: data.poverty },
          { label: 'Classe Média Baixa', value: data.lower_middle },
          { label: 'Classe Média Alta', value: data.upper_middle },
          { label: 'Ricos (10M+)', value: data.rich },
          { label: 'Magnatas (100M+)', value: data.magnates },
          { label: 'Gini Index', value: data.gini_index.toFixed(3) },
          { label: 'Top 1% vs Resto (%)', value: data.top_1_percent_vs_rest.toFixed(1) + '%' },
          { label: 'Distribuição Carteira', value: data.wallet_percent.toFixed(1) + '%' },
          { label: 'Distribuição Banco', value: data.bank_percent.toFixed(1) + '%' },
          { label: 'Distribuição PayPal', value: data.paypal_percent.toFixed(1) + '%' },
        ];
      } catch (e) {
        console.error("Erro ao buscar métricas:", e);
      }
    },
    formatMoney(n) {
      return "R$ " + n.toLocaleString("pt-BR", { minimumFractionDigits: 0 });
    }
  }
}

