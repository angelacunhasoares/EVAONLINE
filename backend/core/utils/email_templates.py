"""
Templates HTML para emails do EVAonline.

Similar ao fluxo do BDMEP/INMET:
1. Email de confirmação: Solicitação recebida, processamento iniciado
2. Email final: Dados processados com arquivo em anexo
"""

from datetime import datetime
from typing import Optional


def get_email_header() -> str:
    """Retorna o cabeçalho padrão dos emails."""
    return """
    <div style="background: linear-gradient(135deg, #1a5f2a 0%, #2d8f4e 100%); 
                padding: 30px 20px; text-align: center; border-radius: 8px 8px 0 0;">
        <h1 style="color: white; margin: 0; font-family: Arial, sans-serif; font-size: 28px;">
            🌱 EVAonline
        </h1>
        <p style="color: #e8f5e9; margin: 10px 0 0 0; font-size: 14px;">
            Web-based global reference EVApotranspiration estimate
        </p>
    </div>
    """


def get_email_footer() -> str:
    """Retorna o rodapé padrão dos emails."""
    return """
    <div style="background: #333; color: #999; padding: 20px; text-align: center; 
                border-radius: 0 0 8px 8px; font-family: Arial, sans-serif; font-size: 12px;">
        <p style="margin: 0 0 10px 0;">
            <strong>EVAonline</strong> - Web-based global reference EVApotranspiration estimate
        </p>
        <p style="margin: 0 0 10px 0; color: #666;">
            FAO-56 Penman-Monteith method | Este é um email automático.
        </p>
        <p style="margin: 0; color: #666;">
            © 2024-2026 EVAonline | 
            <a href="https://github.com/silvianesoares/EVAONLINE" 
               style="color: #4CAF50; text-decoration: none;">GitHub</a>
        </p>
    </div>
    """


def create_processing_started_email(
    task_id: str,
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    started_at: datetime,
    file_format: str = "excel",
) -> tuple[str, str]:
    """
    Cria email de confirmação de que o processamento foi iniciado.
    Similar ao fluxo do BDMEP/INMET.

    Returns:
        tuple: (subject, html_body)
    """
    subject = "📊 EVAonline - Solicitação Recebida | Processamento Iniciado"

    format_label = "Excel (.xlsx)" if file_format == "excel" else "CSV (.csv)"

    # Calcular número de dias
    from datetime import datetime as dt

    start_dt = dt.strptime(start_date, "%Y-%m-%d")
    end_dt = dt.strptime(end_date, "%Y-%m-%d")
    days = (end_dt - start_dt).days + 1

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 8px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            
            {get_email_header()}
            
            <div style="padding: 30px;">
                <h2 style="color: #1a5f2a; margin-top: 0;">
                    ✅ Solicitação Recebida com Sucesso!
                </h2>
                
                <p style="color: #333; line-height: 1.6;">
                    Sua solicitação de dados de evapotranspiração de referência (ETo) foi 
                    recebida e está sendo processada pelo <strong>EVAonline</strong>.
                </p>
                
                <div style="background: #e8f5e9; border-left: 4px solid #4CAF50; 
                            padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                    <p style="margin: 0; color: #2e7d32; font-weight: bold;">
                        📋 Detalhes da Solicitação
                    </p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold; width: 40%;">
                            📍 Localização
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            Lat: {latitude:.4f}° | Lon: {longitude:.4f}°
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            📅 Período Solicitado
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {start_date} a {end_date} ({days} dias)
                        </td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            📎 Formato do Arquivo
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {format_label}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            ⏰ Data/Hora da Solicitação
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {started_at.strftime('%d/%m/%Y às %H:%M:%S')} (UTC-3)
                        </td>
                    </tr>
                </table>
                
                <div style="background: #fff3e0; border-left: 4px solid #ff9800; 
                            padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                    <p style="margin: 0; color: #e65100;">
                        <strong>⏳ Próximos passos:</strong><br>
                        Você receberá outro email com os dados em anexo assim que o 
                        processamento for concluído. O tempo estimado é de 1 a 5 minutos, 
                        dependendo do período solicitado.
                    </p>
                </div>
                
                <p style="color: #666; font-size: 13px; margin-top: 30px;">
                    Caso não receba o email com os dados em até 15 minutos, verifique 
                    sua pasta de spam ou tente novamente.
                </p>
            </div>
            
            {get_email_footer()}
        </div>
    </body>
    </html>
    """

    return subject, html_body


def create_data_ready_email(
    task_id: str,
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    days_processed: int,
    processing_time_seconds: float,
    sources_used: list[str],
    file_format: str = "excel",
    elevation: Optional[float] = None,
    summary_stats: Optional[dict] = None,
) -> tuple[str, str]:
    """
    Cria email informando que os dados estão prontos (com arquivo anexo).

    Returns:
        tuple: (subject, html_body)
    """
    subject = "📊 EVAonline - Seus Dados Estão Prontos! | Download Disponível"

    format_label = "Excel (.xlsx)" if file_format == "excel" else "CSV (.csv)"

    # Mapear nomes das fontes para nomes mais amigáveis
    source_names = {
        "nasa_power": "NASA POWER",
        "openmeteo_archive": "Open-Meteo Archive",
        "openmeteo_forecast": "Open-Meteo Forecast",
        "met_norway": "MET Norway",
    }
    sources_friendly = [source_names.get(s, s) for s in sources_used]
    sources_str = (
        ", ".join(sources_friendly) if sources_friendly else "Múltiplas fontes"
    )

    # Estatísticas resumidas
    stats_html = ""
    if summary_stats:
        eto_mean = summary_stats.get("eto_mean", 0)
        eto_max = summary_stats.get("eto_max", 0)
        eto_min = summary_stats.get("eto_min", 0)
        eto_total = summary_stats.get("eto_total", 0)

        stats_html = f"""
        <div style="background: #e3f2fd; border-left: 4px solid #2196F3; 
                    padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
            <p style="margin: 0 0 10px 0; color: #1565c0; font-weight: bold;">
                📈 Resumo Estatístico
            </p>
            <table style="width: 100%; font-size: 14px;">
                <tr>
                    <td style="padding: 5px 0;"><strong>ETo Médio:</strong></td>
                    <td style="padding: 5px 0;">{eto_mean:.2f} mm/dia</td>
                    <td style="padding: 5px 0;"><strong>ETo Máximo:</strong></td>
                    <td style="padding: 5px 0;">{eto_max:.2f} mm/dia</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0;"><strong>ETo Mínimo:</strong></td>
                    <td style="padding: 5px 0;">{eto_min:.2f} mm/dia</td>
                    <td style="padding: 5px 0;"><strong>ETo Total:</strong></td>
                    <td style="padding: 5px 0;">{eto_total:.2f} mm</td>
                </tr>
            </table>
        </div>
        """

    elevation_str = (
        f"{elevation:.1f} m" if elevation else "Obtida automaticamente"
    )

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 8px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            
            {get_email_header()}
            
            <div style="padding: 30px;">
                <h2 style="color: #1a5f2a; margin-top: 0;">
                    🎉 Seus Dados Estão Prontos!
                </h2>
                
                <p style="color: #333; line-height: 1.6;">
                    O processamento dos seus dados de evapotranspiração de referência (ETo) 
                    foi concluído com sucesso. O arquivo está anexado a este email.
                </p>
                
                <div style="background: #e8f5e9; border-left: 4px solid #4CAF50; 
                            padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                    <p style="margin: 0; color: #2e7d32; font-weight: bold; font-size: 16px;">
                        ✅ Processamento Concluído com Sucesso!
                    </p>
                    <p style="margin: 10px 0 0 0; color: #2e7d32;">
                        {days_processed} dias processados em {processing_time_seconds:.1f} segundos
                    </p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background: #1a5f2a; color: white;">
                        <td colspan="2" style="padding: 12px; font-weight: bold;">
                            📋 Informações do Processamento
                        </td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold; width: 40%;">
                            📍 Localização
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            Lat: {latitude:.4f}° | Lon: {longitude:.4f}°
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            🏔️ Elevação
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {elevation_str}
                        </td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            📅 Período
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {start_date} a {end_date}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            📊 Dias Processados
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {days_processed} dias
                        </td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            🌐 Fontes de Dados
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {sources_str}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            📎 Formato do Arquivo
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {format_label}
                        </td>
                    </tr>
                </table>
                
                {stats_html}
                
                <div style="background: #f5f5f5; padding: 15px; margin: 20px 0; 
                            border-radius: 4px; border: 1px solid #ddd;">
                    <p style="margin: 0 0 10px 0; font-weight: bold; color: #333;">
                        📁 Colunas Disponíveis no Arquivo:
                    </p>
                    <ul style="margin: 0; padding-left: 20px; color: #666; font-size: 13px;">
                        <li><strong>date</strong> - Data da observação</li>
                        <li><strong>tmax_c, tmin_c, tmed_c</strong> - Temperaturas máxima, mínima e média (°C)</li>
                        <li><strong>humidity_pct</strong> - Umidade relativa média (%)</li>
                        <li><strong>wind_ms</strong> - Velocidade do vento a 2m (m/s)</li>
                        <li><strong>radiation_mj_m2</strong> - Radiação solar global (MJ/m²/dia)</li>
                        <li><strong>precip_mm</strong> - Precipitação acumulada (mm)</li>
                        <li><strong>et0_mm_day</strong> - Evapotranspiração de referência (mm/dia)</li>
                    </ul>
                </div>
            </div>
            
            {get_email_footer()}
        </div>
    </body>
    </html>
    """

    return subject, html_body


def create_processing_error_email(
    task_id: str,
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    error_message: str,
) -> tuple[str, str]:
    """
    Cria email informando erro no processamento.

    Returns:
        tuple: (subject, html_body)
    """
    subject = "⚠️ EVAonline - Erro no Processamento | Tente Novamente"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 20px auto; background: white; border-radius: 8px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            
            {get_email_header()}
            
            <div style="padding: 30px;">
                <h2 style="color: #c62828; margin-top: 0;">
                    ⚠️ Erro no Processamento
                </h2>
                
                <p style="color: #333; line-height: 1.6;">
                    Caro(a) usuário(a), infelizmente ocorreu um erro ao processar 
                    sua solicitação de dados.
                </p>
                
                <div style="background: #ffebee; border-left: 4px solid #f44336; 
                            padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                    <p style="margin: 0; color: #c62828; font-weight: bold;">
                        ❌ Detalhes do Erro
                    </p>
                    <p style="margin: 10px 0 0 0; color: #c62828; font-family: monospace; 
                              font-size: 13px; word-break: break-all;">
                        {error_message[:500]}
                    </p>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold; width: 40%;">
                            🆔 ID da Solicitação
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd; font-family: monospace;">
                            {task_id[:8]}...
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            📍 Localização
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            Lat: {latitude:.4f}° | Lon: {longitude:.4f}°
                        </td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 12px; border: 1px solid #ddd; font-weight: bold;">
                            📅 Período Solicitado
                        </td>
                        <td style="padding: 12px; border: 1px solid #ddd;">
                            {start_date} a {end_date}
                        </td>
                    </tr>
                </table>
                
                <div style="background: #e3f2fd; border-left: 4px solid #2196F3; 
                            padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                    <p style="margin: 0; color: #1565c0;">
                        <strong>💡 Sugestões:</strong><br>
                        • Tente reduzir o período solicitado<br>
                        • Verifique se as coordenadas estão corretas<br>
                        • Aguarde alguns minutos e tente novamente<br>
                        • Se o problema persistir, entre em contato conosco
                    </p>
                </div>
            </div>
            
            {get_email_footer()}
        </div>
    </body>
    </html>
    """

    return subject, html_body
