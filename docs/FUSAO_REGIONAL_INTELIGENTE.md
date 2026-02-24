# 🔬 Fusão de Dados Climáticos — Filtro de Kalman

**Versão:** 2.0  
**Última atualização:** 2025-02-23

---

## Visão Geral

O EVAonline utiliza um **Filtro de Kalman** para fusão ótima de dados climáticos provenientes de múltiplas fontes. Esta abordagem permite combinar dados com diferentes níveis de qualidade, resolução temporal e cobertura geográfica, gerando uma estimativa ótima com incerteza quantificada.

---

## Fontes de Dados

| Fonte | Cobertura | Tipo | Qualidade Base |
|-------|-----------|------|---------------|
| NASA POWER | Global | Satélite + Reanálise | 0.90 |
| Open-Meteo | Global | Reanálise (ERA5) + Previsão | 0.85 |
| MET Norway | Global (otimizado Nordic) | Previsão | 0.80 |
| NWS Forecast | EUA apenas | Previsão | 0.75 |
| NWS Stations | EUA apenas | Observações in-situ | 0.85 |

---

## Algoritmo de Fusão

### Variáveis Fusionadas

O vetor de estado contém 7 variáveis meteorológicas:

$$\mathbf{x} = [T_{max}, T_{min}, T_{mean}, RH, u_2, R_s, P]^T$$

Onde:
- $T_{max}, T_{min}, T_{mean}$ — Temperaturas máxima, mínima e média (°C)
- $RH$ — Umidade relativa (%)
- $u_2$ — Velocidade do vento a 2m (m/s)
- $R_s$ — Radiação solar (MJ/m²/dia)
- $P$ — Pressão atmosférica (kPa)

### Etapas do Filtro

#### 1. Predição

$$\hat{\mathbf{x}}^- = F \cdot \hat{\mathbf{x}}^+_{k-1}$$
$$P^- = F \cdot P^+_{k-1} \cdot F^T + Q$$

Onde:
- $F$ = Matriz de transição (identidade para variáveis diárias)
- $Q$ = Covariância do ruído de processo (estimada da variabilidade entre fontes)
- $P$ = Covariância do erro de estimativa

#### 2. Atualização (para cada fonte disponível)

Para cada fonte $i$ que possui dados:

$$\tilde{\mathbf{y}}_i = \mathbf{z}_i - H \cdot \hat{\mathbf{x}}^-$$
$$S_i = H \cdot P^- \cdot H^T + R_i$$
$$K_i = P^- \cdot H^T \cdot S_i^{-1}$$
$$\hat{\mathbf{x}}^+ = \hat{\mathbf{x}}^- + K_i \cdot \tilde{\mathbf{y}}_i$$
$$P^+ = (I - K_i \cdot H) \cdot P^-$$

Onde:
- $\mathbf{z}_i$ = Medição da fonte $i$
- $R_i$ = Covariância do ruído de medição da fonte $i$ (baseado na qualidade)
- $K_i$ = Ganho de Kalman (pesos ótimos)
- $\tilde{\mathbf{y}}_i$ = Inovação (diferença entre medição e predição)

#### 3. Detecção de Outliers

A sequência de inovação é monitorada:

$$|\tilde{\mathbf{y}}_i| > 3\sqrt{S_i} \Rightarrow \text{outlier detectado}$$

Medições identificadas como outliers recebem peso reduzido (R aumentado).

### Matriz de Ruído de Medição (R)

A matriz R é calibrada para cada fonte com base em:

| Fator | Impacto em R |
|-------|-------------|
| Qualidade base da fonte | R inversamente proporcional |
| Completude dos dados | Dados faltantes aumentam R |
| Consistência física | Valores fora de faixas aumentam R |
| Tipo de dado (obs. vs forecast) | Observações têm menor R |

---

## Modos de Operação

### Modo Recent (7 dias)

```
Fontes disponíveis: NASA POWER + Open-Meteo + MET Norway [+ NWS se EUA]
Estratégia: Fusão completa de todas as fontes disponíveis
Peso maior: NASA POWER (latência ~3 dias) + Open-Meteo (tempo real)
```

### Modo Historical (período customizado)

```
Fontes disponíveis: NASA POWER + Open-Meteo Archive
Estratégia: Fusão dual com alta confiança
Peso maior: NASA POWER (dados validados por satélite)
Período: 1981-presente (NASA POWER) / 1940-presente (Open-Meteo ERA5)
```

### Modo Forecast (7 dias)

```
Fontes disponíveis: Open-Meteo Forecast + MET Norway [+ NWS se EUA]
Estratégia: Fusão de previsões com peso por horizonte temporal
Peso maior: Previsões de curto prazo (1-3 dias)
```

---

## Fluxo de Implementação

```
1. source_manager.py → Coleta dados de TODAS as fontes (paralelo, async)
2. Cada fonte retorna DataFrame padronizado
3. kalman_fusion.py → Inicializa estado com primeira fonte disponível
4. Para cada dia no período:
   a. Predição do estado (baseado no dia anterior)
   b. Para cada fonte com dados neste dia:
      - Calcula inovação
      - Verifica outliers
      - Atualiza estado com ganho de Kalman
   c. Armazena estimativa fusionada + incerteza
5. Retorna DataFrame fusionado → eto_calculator.py
```

---

## Validação

O sistema de fusão foi validado usando o dataset EVAonline Validation v1.0.0 (publicado no Zenodo):

- **17 cidades** na região MATOPIBA (Brasil)
- **Período**: 1991–2020
- **Métricas**: RMSE, MAE, R², NSE, PBIAS
- **Comparação**: ETo NASA-only vs ETo Open-Meteo-only vs ETo fusionado

### Resultados

| Comparação | RMSE (mm/dia) | R² | NSE |
|-----------|---------------|-----|------|
| NASA-only vs Referência | ~0.5-0.8 | >0.85 | >0.80 |
| OpenMeteo-only vs Referência | ~0.6-1.0 | >0.80 | >0.75 |
| Fusionado vs Referência | ~0.4-0.6 | >0.90 | >0.85 |

> O dado fusionado consistentemente supera qualquer fonte individual.

---

## Limitações

1. **Sem dados de estações locais**: A fusão não inclui dados de estações meteorológicas de superfície (exceto NWS para EUA)
2. **Kalman linear**: Utiliza filtro de Kalman linear (não EKF/UKF) — adequado para variáveis meteorológicas diárias
3. **Q estática**: A covariância de processo Q é estimada uma vez por cálculo, não adaptativa
4. **Sem assimilação**: Não incorpora modelos meteorológicos dinâmicos na predição

---

**Última atualização:** 2025-02-23  
**Versão:** 2.0