import numpy as np
import pandas as pd
import plotly.graph_objects as go
from loguru import logger

from shared_utils.get_translations import get_translations


def plot_eto_vs_temperature(df: pd.DataFrame, lang: str = "pt") -> go.Figure:
    """
    Gera um gráfico de barras para ETo e linhas para temperaturas
    máxima e mínima.

    Parâmetros:
    - df: DataFrame com os dados (espera colunas 'date', 'T2M_MAX',
          'T2M_MIN', 'ETo').
    - lang: Idioma para traduções ('pt' ou 'en').

    Retorna:
    - Objeto go.Figure com o gráfico.
    """
    try:
        if df is None or df.empty:
            logger.warning(
                "DataFrame vazio ou None fornecido para "
                "plot_eto_vs_temperature"
            )
            return go.Figure()

        # Obter traduções
        t = get_translations(lang)

        # Support both old 'ETo' and new 'eto_evaonline' column names
        eto_col = "eto_evaonline" if "eto_evaonline" in df.columns else "ETo"
        expected_columns = ["date", "T2M_MAX", "T2M_MIN", eto_col]
        missing_columns = [
            col for col in expected_columns if col not in df.columns
        ]
        if missing_columns:
            logger.error(f"Colunas ausentes no DataFrame: {missing_columns}")
            return go.Figure()  # Return empty figure instead of raising

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df["date"],
                y=df[eto_col],
                name=t["eto"],
                marker_color="#005B99",  # Cor alinhada com o tema
                text=df[eto_col].round(2),
                textposition="outside",
                textfont={"size": 12},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["T2M_MAX"],
                mode="lines",
                name=t["temp_max"],
                line={"color": "red"},
                textfont={"size": 12},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["T2M_MIN"],
                mode="lines",
                name=t["temp_min"],
                line={"color": "green"},
                textfont={"size": 12},
            )
        )
        fig.update_layout(
            title={"text": t["eto_vs_temp"], "x": 0.5, "xanchor": "center"},
            xaxis_tickfont_size=12,
            yaxis={"title": {"text": t["temperature"], "font": {"size": 12}}},
            xaxis={"tickangle": 45, "title": t["date"]},
            legend_title=t["legend"],
            barmode="group",
            legend={
                "x": 1.0,
                "y": -0.3,
                "xanchor": "right",
                "yanchor": "top",
                "orientation": "h",
            },
            template="plotly_white",
            margin={"b": 150},
            height=500,  # Fixed height to prevent infinite growth
        )
        logger.info("Gráfico ET₀ vs. Temperatura gerado com sucesso")
        return fig

    except Exception as e:
        logger.error(f"Erro ao gerar gráfico ET₀ vs. Temperatura: {str(e)}")
        return go.Figure()


def plot_eto_vs_radiation(df: pd.DataFrame, lang: str = "pt") -> go.Figure:
    """
    Gera um gráfico de linhas para ETo e radiação solar com eixos Y
    duplos.

    Parâmetros:
    - df: DataFrame com os dados (espera colunas 'date',
          'ALLSKY_SFC_SW_DWN', 'ETo').
    - lang: Idioma para traduções ('pt' ou 'en').

    Retorna:
    - Objeto go.Figure com o gráfico.
    """
    try:
        if df is None or df.empty:
            logger.warning(
                "DataFrame vazio ou None fornecido para "
                "plot_eto_vs_radiation"
            )
            return go.Figure()

        t = get_translations(lang)

        # Support both old 'ETo' and new 'eto_evaonline' column names
        eto_col = "eto_evaonline" if "eto_evaonline" in df.columns else "ETo"
        expected_columns = ["date", "ALLSKY_SFC_SW_DWN", eto_col]
        missing_columns = [
            col for col in expected_columns if col not in df.columns
        ]
        if missing_columns:
            logger.error(f"Colunas ausentes no DataFrame: {missing_columns}")
            return go.Figure()  # Return empty figure instead of raising

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df[eto_col],
                mode="lines",
                name=t["eto"],
                yaxis="y1",
                line={"color": "#005B99"},
                textfont={"size": 12},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["ALLSKY_SFC_SW_DWN"],
                mode="lines",
                name=t["radiation"],
                yaxis="y2",
                line={"color": "orange"},
                textfont={"size": 12},
            )
        )
        fig.update_layout(
            title={"text": t["eto_vs_rad"], "x": 0.5, "xanchor": "center"},
            xaxis_tickfont_size=12,
            yaxis={"title": {"text": t["eto"], "font": {"size": 12}}},
            yaxis2={
                "title": t["radiation"],
                "overlaying": "y",
                "side": "right",
            },
            legend_title=t["legend"],
            legend={
                "x": 1.0,
                "y": -0.3,
                "xanchor": "right",
                "yanchor": "top",
                "orientation": "h",
            },
            template="plotly_white",
            margin={"b": 150},
            height=500,  # Fixed height to prevent infinite growth
        )
        logger.info("Gráfico ET₀ vs. Radiação gerado com sucesso")
        return fig

    except Exception as e:
        logger.error(f"Erro ao gerar gráfico ET₀ vs. Radiação: {str(e)}")
        return go.Figure()


def plot_temp_rad_prec(df: pd.DataFrame, lang: str = "pt") -> go.Figure:
    """
    Gera um gráfico combinado de barras (ETo, precipitação) e linhas
    (temp. máx., radiação).

    Parâmetros:
    - df: DataFrame com os dados (espera colunas 'date', 'T2M_MAX',
          'ALLSKY_SFC_SW_DWN', 'PRECTOTCORR', 'ETo').
    - lang: Idioma para traduções ('pt' ou 'en').

    Retorna:
    - Objeto go.Figure com o gráfico.
    """
    try:
        if df is None or df.empty:
            logger.warning(
                "DataFrame vazio ou None fornecido para " "plot_temp_rad_prec"
            )
            return go.Figure()

        t = get_translations(lang)

        # Support both old 'ETo' and new 'eto_evaonline' column names
        eto_col = "eto_evaonline" if "eto_evaonline" in df.columns else "ETo"
        expected_columns = [
            "date",
            "T2M_MAX",
            "ALLSKY_SFC_SW_DWN",
            "PRECTOTCORR",
            eto_col,
        ]
        missing_columns = [
            col for col in expected_columns if col not in df.columns
        ]
        if missing_columns:
            logger.error(f"Colunas ausentes no DataFrame: {missing_columns}")
            return go.Figure()  # Return empty figure instead of raising

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df["date"],
                y=df[eto_col],
                name=t["eto"],
                marker_color="#005B99",
                text=df[eto_col].round(2),
                textposition="outside",
                textfont={"size": 12},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["T2M_MAX"],
                mode="lines",
                name=t["temp_max"],
                line={"color": "red"},
                yaxis="y2",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["ALLSKY_SFC_SW_DWN"],
                mode="lines",
                name=t["radiation"],
                line={"color": "green"},
                yaxis="y3",
            )
        )
        fig.add_trace(
            go.Bar(
                x=df["date"],
                y=df["PRECTOTCORR"],
                name=t["precipitation"],
                marker_color="purple",
                text=df["PRECTOTCORR"].round(2),
                textposition="outside",
                textfont={"size": 12},
            )
        )

        temp_max = df["T2M_MAX"].max()
        temp_max_range = temp_max * 1.2 if temp_max > 0 else 10

        rad_max = df["ALLSKY_SFC_SW_DWN"].max()
        rad_range = rad_max * 1.2 if rad_max > 0 else 10

        eto_max = df[eto_col].max()
        precip_max = df["PRECTOTCORR"].max()
        bar_max = (
            max(eto_max, precip_max) * 1.5
            if max(eto_max, precip_max) > 0
            else 10
        )

        fig.update_layout(
            title={"text": t["temp_rad_prec"], "x": 0.5, "xanchor": "center"},
            xaxis={"title": t["date"], "tickangle": -45},
            yaxis={
                "title": f"{t['eto']}/{t['precipitation']} (mm/dia)",
                "side": "left",
                "range": [0, bar_max],
            },
            yaxis2={
                "title": t["temp_max"],
                "overlaying": "y",
                "side": "right",
                "range": [0, temp_max_range],
            },
            yaxis3={
                "title": t["radiation"],
                "overlaying": "y",
                "side": "right",
                "range": [0, rad_range],
                "anchor": "free",
                "position": 0.85,
            },
            legend={
                "x": 1.0,
                "y": -0.3,
                "xanchor": "right",
                "yanchor": "top",
                "orientation": "h",
            },
            barmode="group",
            template="plotly_white",
            margin={"b": 150},
            height=500,  # Fixed height to prevent infinite growth
        )
        logger.info("Gráfico combinado gerado com sucesso")
        return fig

    except Exception as e:
        logger.error(f"Erro ao gerar gráfico Temp/Rad/Prec: {str(e)}")
        return go.Figure()


def plot_heatmap(df: pd.DataFrame, lang: str = "pt") -> go.Figure:
    """
    Gera um mapa de calor para a matriz de correlação.

    Parâmetros:
    - df: DataFrame com os dados (espera colunas numéricas, exceto
          'date' e 'PRECTOTCORR').
    - lang: Idioma para traduções ('pt' ou 'en').

    Retorna:
    - Objeto go.Figure com o gráfico.
    """
    try:
        if df is None or df.empty:
            logger.warning(
                "DataFrame vazio ou None fornecido para plot_heatmap"
            )
            return go.Figure()

        t = get_translations(lang)
        columns_to_exclude = ["date", "PRECTOTCORR"]
        corr_columns = [
            col for col in df.columns if col not in columns_to_exclude
        ]
        if not corr_columns:
            logger.error("Nenhuma coluna válida para calcular correlação")
            raise ValueError("Nenhuma coluna válida para calcular correlação")

        corr_matrix = df[corr_columns].corr().round(2)
        # Renomear colunas para traduções
        translated_columns = {
            col: t.get(col.lower(), col) for col in corr_matrix.columns
        }
        corr_matrix = corr_matrix.rename(
            columns=translated_columns, index=translated_columns
        )

        fig = go.Figure()
        fig.add_heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            text=corr_matrix.values,
            texttemplate="%{text}",
            textfont={"size": 10},
        )
        fig.update_layout(
            title={"text": t["heatmap"], "x": 0.5, "xanchor": "center"},
            template="plotly_white",
            margin={"b": 100},
            height=500,  # Fixed height to prevent infinite growth
        )
        logger.info("Mapa de calor gerado com sucesso")
        return fig

    except Exception as e:
        logger.error(f"Erro ao gerar mapa de calor: {str(e)}")
        return go.Figure()


def plot_correlation(
    df: pd.DataFrame, x_var: str, lang: str = "pt"
) -> go.Figure:
    """
    Gera um gráfico de dispersão com linha de tendência para uma
    variável vs. ETo.

    Parâmetros:
    - df: DataFrame com os dados (espera colunas 'ETo' e x_var).
    - x_var: Nome da coluna para o eixo X.
    - lang: Idioma para traduções ('pt' ou 'en').

    Retorna:
    - Objeto go.Figure com o gráfico.
    """
    try:
        if df is None or df.empty:
            logger.warning(
                "DataFrame vazio ou None fornecido para plot_correlation"
            )
            return go.Figure()

        t = get_translations(lang)
        if x_var not in df.columns or "ETo" not in df.columns:
            logger.error(
                f"Colunas inválidas para correlação: x_var={x_var}, ETo"
            )
            raise ValueError(
                f"Colunas inválidas para correlação: x_var={x_var}, ETo"
            )

        x_var_translated = t.get(x_var.lower(), x_var)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df[x_var],
                y=df["ETo"],
                mode="markers",
                name=f"{x_var_translated} vs. {t['eto']}",
                marker={"color": "#005B99"},
            )
        )
        slope, intercept = np.polyfit(df[x_var], df["ETo"], 1)
        line = slope * df[x_var] + intercept

        fig.add_trace(
            go.Scatter(
                x=df[x_var],
                y=line,
                mode="lines",
                name=t["trend_line"],
                line={"color": "red", "dash": "dash"},
            )
        )

        fig.update_layout(
            xaxis_title=x_var_translated,
            yaxis_title=t["eto"],
            title={
                "text": (
                    f"{t['correlation']}: {x_var_translated} vs. {t['eto']}"
                ),
                "x": 0.5,
                "xanchor": "center",
            },
            legend={
                "x": 1.0,
                "y": -0.3,
                "xanchor": "right",
                "yanchor": "top",
                "orientation": "h",
                "font": {"size": 12},
            },
            template="plotly_white",
            margin={"b": 100},
            height=500,  # Fixed height to prevent infinite growth
        )
        logger.info(
            f"Gráfico de correlação gerado com sucesso: {x_var} vs. ETo"
        )
        return fig

    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de correlação: {str(e)}")
        return go.Figure()
