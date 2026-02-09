import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="Blūmi Talents - Agenda de Eventos",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ESTILO CSS PERSONALIZADO =====
st.markdown("""
<style>
    /* Importar fonte Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Aplicar fonte globalmente */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fundo geral */
    .main {
        background-color: #F2F4F6;
        padding: 48px 24px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        padding: 32px 16px;
    }
    
    /* Títulos */
    h1 {
        color: #3B4B5E;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 8px;
    }
    
    h2 {
        color: #3B4B5E;
        font-weight: 600;
        font-size: 1.8rem;
        margin-top: 32px;
        margin-bottom: 24px;
    }
    
    h3 {
        color: #3B4B5E;
        font-weight: 600;
        font-size: 1.3rem;
        margin-bottom: 16px;
    }
    
    /* Cards de seção */
    .section-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    
    /* Cards de eventos */
    .event-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    
    .event-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Cores das tags de tipo de evento */
    .event-card.feira { border-left-color: #FF6B8A; }
    .event-card.live { border-left-color: #00D9FF; }
    .event-card.circle { border-left-color: #D4FF33; }
    .event-card.outros { border-left-color: #9E9E9E; }
    
    /* Tags de tipo */
    .event-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .tag-feira { background-color: #FFE5EC; color: #C91952; }
    .tag-live { background-color: #E0F9FF; color: #007A8C; }
    .tag-circle { background-color: #F5FFD6; color: #5A6B00; }
    .tag-outros { background-color: #F5F5F5; color: #424242; }
    
    /* Botão secundário customizado */
    .stButton > button {
        background-color: #FFFFFF;
        color: #3B4B5E;
        border: 1px solid #D8DEE6;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #F2F4F6;
        border-color: #3B4B5E;
    }
    
    /* Calendário */
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-top: 16px;
    }
    
    .calendar-day {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 12px 8px;
        text-align: center;
        min-height: 100px;
        position: relative;
        border: 1px solid #E8EBF0;
    }
    
    .calendar-day-header {
        font-weight: 600;
        color: #3B4B5E;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }
    
    .calendar-day-number {
        font-size: 1.1rem;
        color: #3B4B5E;
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .calendar-day.has-event {
        background-color: #F0FFF4;
        border-color: #D4FF33;
    }
    
    .calendar-day.today {
        background-color: #E0F9FF;
        border-color: #00D9FF;
        border-width: 2px;
    }
    
    .event-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin: 2px;
    }
    
    /* Remover padding padrão */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #3B4B5E;
    }
    
    /* Filtros na sidebar */
    .sidebar-filter-section {
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# ===== FUNÇÃO DE CARREGAMENTO DE DADOS =====
@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_events_from_csv():
    """Carrega os eventos do CSV público do Google Sheets"""
    try:
        # URL do CSV público - ABA: Registro_eventos
        # IMPORTANTE: Certifique-se de que a aba "Registro_eventos" está publicada
        CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaDzfwhQrA8vGBdTYMQxMtWE-ABiSDqBpxxfVQMrJcvNC0sSqOEH6wj7Gvk3oTQhDzMJmWFEw3yQyL/pub?output=csv"
        
        # Carregar dados com timeout
        df = pd.read_csv(CSV_URL, encoding='utf-8')
        
        # Verificar se tem as colunas esperadas
        expected_cols = ['Nome', 'Data início', 'Data Final', 'Tipo de evento', 'Universidade']
        missing_cols = [col for col in expected_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"⚠️ Colunas faltando na planilha: {missing_cols}")
            st.info("📌 Verifique se a aba 'Registro_eventos' está sendo publicada como CSV")
            return None
        
        # Processar datas
        df['Data início'] = pd.to_datetime(df['Data início'], errors='coerce', dayfirst=True)
        df['Data Final'] = pd.to_datetime(df['Data Final'], errors='coerce', dayfirst=True)
        
        # Remover linhas completamente vazias
        df = df.dropna(how='all')
        
        return df
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        st.info("""
        **Possíveis causas:**
        1. A aba 'Registro_eventos' não está publicada como CSV
        2. URL do CSV incorreta
        3. Problema de conexão com o Google Sheets
        
        **Como resolver:**
        - Vá em Arquivo → Compartilhar → Publicar na Web
        - Selecione a aba 'Registro_eventos'
        - Formato: CSV
        - Publique e use o novo link
        """)
        return None

def get_event_color(tipo_evento):
    """Retorna a cor correspondente ao tipo de evento"""
    if pd.isna(tipo_evento):
        return '#9E9E9E', 'outros'
    
    tipo_lower = str(tipo_evento).lower()
    
    if 'feira' in tipo_lower:
        return '#FF6B8A', 'feira'
    elif 'live' in tipo_lower:
        return '#00D9FF', 'live'
    elif 'circle' in tipo_lower or 'círculo' in tipo_lower:
        return '#D4FF33', 'circle'
    else:
        return '#9E9E9E', 'outros'

def get_event_tag_class(tipo_evento):
    """Retorna a classe CSS para a tag do tipo de evento"""
    if pd.isna(tipo_evento):
        return 'tag-outros'
    
    tipo_lower = str(tipo_evento).lower()
    
    if 'feira' in tipo_lower:
        return 'tag-feira'
    elif 'live' in tipo_lower:
        return 'tag-live'
    elif 'circle' in tipo_lower or 'círculo' in tipo_lower:
        return 'tag-circle'
    else:
        return 'tag-outros'

# ===== INTERFACE PRINCIPAL =====
def main():
    # Cabeçalho
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div style='margin-bottom: 32px;'>
            <h1>📅 Agenda de Eventos Blūmi</h1>
            <p style='color: #6B7A8F; font-size: 1.1rem;'>
                Acompanhe todos os eventos, feiras e ações da Blūmi Talents
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.link_button(
            "📊 Abrir Planilha",
            "https://docs.google.com/spreadsheets/d/1J7baToo2UjdEJp8jtWc_7tYdQN_kJPmErKIR_9ByvL4/edit",
            use_container_width=True
        )
    
    # Carregar dados
    with st.spinner("⏳ Carregando eventos da planilha..."):
        df = load_events_from_csv()
    
    if df is None:
        st.stop()
    
    if df.empty:
        st.warning("⚠️ Nenhum evento encontrado na planilha.")
        st.info("Verifique se a aba 'Registro_eventos' tem dados e está publicada corretamente.")
        st.stop()
    
    # ===== SIDEBAR - FILTROS =====
    with st.sidebar:
        st.markdown("### 🎯 Filtros")
        
        # Filtro por tipo de evento
        tipos_evento = ['Todos'] + sorted(df['Tipo de evento'].dropna().unique().tolist())
        tipo_selecionado = st.selectbox(
            "Tipo de Evento",
            tipos_evento,
            index=0
        )
        
        # Filtro por mês
        meses = {
            'Todos': None,
            'Janeiro': 1, 'Fevereiro': 2, 'Março': 3, 'Abril': 4,
            'Maio': 5, 'Junho': 6, 'Julho': 7, 'Agosto': 8,
            'Setembro': 9, 'Outubro': 10, 'Novembro': 11, 'Dezembro': 12
        }
        mes_selecionado = st.selectbox(
            "Mês",
            list(meses.keys()),
            index=0
        )
        
        # Filtro por universidade
        universidades = ['Todas'] + sorted(df['Universidade'].dropna().unique().tolist())
        universidade_selecionada = st.selectbox(
            "Universidade",
            universidades,
            index=0
        )
        
        st.markdown("---")
        st.markdown("""
        <div style='padding: 16px; background-color: #F2F4F6; border-radius: 10px; margin-top: 24px;'>
            <p style='color: #6B7A8F; font-size: 0.85rem; margin: 0;'>
                📍 Dados atualizados em tempo real<br>
                🔄 Atualização automática a cada 5 minutos
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo de evento'] == tipo_selecionado]
    
    if mes_selecionado != 'Todos':
        mes_num = meses[mes_selecionado]
        df_filtrado = df_filtrado[df_filtrado['Data início'].dt.month == mes_num]
    
    if universidade_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Universidade'] == universidade_selecionada]
    
    # ===== MÉTRICAS =====
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📅 Total de Eventos", len(df_filtrado))
    
    with col2:
        eventos_mes = len(df_filtrado[df_filtrado['Data início'].dt.month == datetime.now().month])
        st.metric("📆 Eventos este Mês", eventos_mes)
    
    with col3:
        eventos_futuros = len(df_filtrado[df_filtrado['Data início'] >= datetime.now()])
        st.metric("🔜 Próximos Eventos", eventos_futuros)
    
    with col4:
        universidades_unicas = df_filtrado['Universidade'].nunique()
        st.metric("🎓 Universidades", universidades_unicas)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ===== VISUALIZAÇÃO =====
    tab1, tab2 = st.tabs(["📋 Lista de Eventos", "📅 Visão Calendário"])
    
    with tab1:
        # Lista de eventos
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### Próximos Eventos")
        
        if len(df_filtrado) == 0:
            st.info("Nenhum evento encontrado com os filtros selecionados.")
        else:
            # Ordenar por data
            df_ordenado = df_filtrado.sort_values('Data início')
            
            for idx, row in df_ordenado.iterrows():
                color, tipo_class = get_event_color(row['Tipo de evento'])
                tag_class = get_event_tag_class(row['Tipo de evento'])
                
                data_inicio = row['Data início']
                data_fim = row['Data Final']
                
                # Formatar datas
                if pd.notna(data_inicio):
                    data_inicio_str = data_inicio.strftime('%d/%m/%Y')
                else:
                    data_inicio_str = 'Data não definida'
                
                if pd.notna(data_fim):
                    data_fim_str = data_fim.strftime('%d/%m/%Y')
                else:
                    data_fim_str = data_inicio_str
                
                tipo_evento_display = row['Tipo de evento'] if pd.notna(row['Tipo de evento']) else 'Não definido'
                universidade_display = row['Universidade'] if pd.notna(row['Universidade']) else 'Não definida'
                
                st.markdown(f"""
                <div class="event-card {tipo_class}">
                    <div style="margin-bottom: 8px;">
                        <span class="event-tag {tag_class}">{tipo_evento_display}</span>
                    </div>
                    <h3 style="margin: 8px 0; font-size: 1.1rem;">{row['Nome']}</h3>
                    <div style="color: #6B7A8F; font-size: 0.9rem;">
                        📅 {data_inicio_str} até {data_fim_str}<br>
                        🎓 {universidade_display}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # Visão de calendário
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        
        # Controles do calendário
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            ano_cal = st.selectbox("Ano", range(2024, 2027), index=1, key="ano_cal")
        
        with col2:
            meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            mes_cal = st.selectbox("Mês", range(1, 13), 
                                   format_func=lambda x: meses_pt[x-1],
                                   index=datetime.now().month - 1,
                                   key="mes_cal")
        
        with col3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("📅 Hoje", use_container_width=True):
                st.rerun()
        
        st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
        
        # Título do mês
        st.markdown(f"""
        <h2 style='text-align: center; color: #3B4B5E; font-weight: 600; margin-bottom: 24px;'>
            {meses_pt[mes_cal-1]} {ano_cal}
        </h2>
        """, unsafe_allow_html=True)
        
        # Gerar calendário
        cal = calendar.monthcalendar(ano_cal, mes_cal)
        
        # Header do calendário (dias da semana)
        dias_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
        
        header_html = """
        <div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 4px;'>
        """
        for dia in dias_semana:
            header_html += f"""
            <div style='text-align: center; padding: 12px; font-weight: 600; 
                        color: #6B7A8F; font-size: 0.9rem; background-color: #F2F4F6;
                        border-radius: 8px;'>
                {dia}
            </div>
            """
        header_html += "</div>"
        st.markdown(header_html, unsafe_allow_html=True)
        
        # Grid do calendário
        hoje = datetime.now().date()
        
        calendar_html = """
        <div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px;'>
        """
        
        for semana in cal:
            for dia in semana:
                if dia == 0:
                    # Dia vazio (do mês anterior/posterior)
                    calendar_html += """
                    <div style='background-color: #FAFBFC; border-radius: 8px; 
                                min-height: 100px; padding: 8px; border: 1px solid #E8EBF0;'>
                    </div>
                    """
                else:
                    data_dia = datetime(ano_cal, mes_cal, dia).date()
                    
                    # Verificar eventos neste dia
                    eventos_dia = df_filtrado[
                        (df_filtrado['Data início'].dt.date <= data_dia) &
                        (df_filtrado['Data Final'].dt.date >= data_dia)
                    ]
                    
                    # Estilo do dia
                    is_today = data_dia == hoje
                    has_events = len(eventos_dia) > 0
                    
                    # Background color
                    if is_today:
                        bg_color = "#E0F9FF"
                        border_color = "#00D9FF"
                        border_width = "2px"
                    elif has_events:
                        bg_color = "#FFFFFF"
                        border_color = "#D4FF33"
                        border_width = "2px"
                    else:
                        bg_color = "#FFFFFF"
                        border_color = "#E8EBF0"
                        border_width = "1px"
                    
                    calendar_html += f"""
                    <div style='background-color: {bg_color}; border-radius: 8px; 
                                min-height: 100px; padding: 8px; border: {border_width} solid {border_color};
                                position: relative;'>
                        <div style='font-weight: 600; color: #3B4B5E; font-size: 1rem; 
                                    margin-bottom: 8px;'>
                            {dia}
                        </div>
                    """
                    
                    # Adicionar eventos (máximo 3 visíveis)
                    eventos_exibir = min(3, len(eventos_dia))
                    for idx, (_, evento) in enumerate(eventos_dia.head(eventos_exibir).iterrows()):
                        color, tipo_class = get_event_color(evento['Tipo de evento'])
                        nome_evento = evento['Nome']
                        
                        # Truncar nome se muito longo
                        if len(nome_evento) > 20:
                            nome_evento = nome_evento[:17] + "..."
                        
                        calendar_html += f"""
                        <div style='background-color: {color}; color: white; 
                                    padding: 4px 6px; margin-bottom: 4px; border-radius: 4px;
                                    font-size: 0.7rem; font-weight: 600; 
                                    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>
                            {nome_evento}
                        </div>
                        """
                    
                    # Indicador de mais eventos
                    if len(eventos_dia) > 3:
                        calendar_html += f"""
                        <div style='font-size: 0.65rem; color: #6B7A8F; font-weight: 600; 
                                    margin-top: 4px;'>
                            +{len(eventos_dia) - 3} mais
                        </div>
                        """
                    
                    calendar_html += "</div>"
        
        calendar_html += "</div>"
        st.markdown(calendar_html, unsafe_allow_html=True)
        
        # Legenda
        st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style='padding: 16px; background-color: #F2F4F6; border-radius: 10px;'>
                <strong style='color: #3B4B5E; font-size: 0.9rem;'>Legenda de Cores:</strong><br><br>
                <div style='margin: 8px 0;'>
                    <span style='display: inline-block; width: 16px; height: 16px; 
                                 background-color: #FF6B8A; border-radius: 4px; margin-right: 8px;
                                 vertical-align: middle;'></span>
                    <span style='color: #3B4B5E; font-size: 0.85rem;'>Feiras</span>
                </div>
                <div style='margin: 8px 0;'>
                    <span style='display: inline-block; width: 16px; height: 16px; 
                                 background-color: #00D9FF; border-radius: 4px; margin-right: 8px;
                                 vertical-align: middle;'></span>
                    <span style='color: #3B4B5E; font-size: 0.85rem;'>Lives</span>
                </div>
                <div style='margin: 8px 0;'>
                    <span style='display: inline-block; width: 16px; height: 16px; 
                                 background-color: #D4FF33; border-radius: 4px; margin-right: 8px;
                                 vertical-align: middle;'></span>
                    <span style='color: #3B4B5E; font-size: 0.85rem;'>Circles</span>
                </div>
                <div style='margin: 8px 0;'>
                    <span style='display: inline-block; width: 16px; height: 16px; 
                                 background-color: #9E9E9E; border-radius: 4px; margin-right: 8px;
                                 vertical-align: middle;'></span>
                    <span style='color: #3B4B5E; font-size: 0.85rem;'>Outros</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='padding: 16px; background-color: #F2F4F6; border-radius: 10px;'>
                <strong style='color: #3B4B5E; font-size: 0.9rem;'>Destaque:</strong><br><br>
                <div style='margin: 8px 0;'>
                    <span style='display: inline-block; width: 16px; height: 16px; 
                                 background-color: #E0F9FF; border: 2px solid #00D9FF; 
                                 border-radius: 4px; margin-right: 8px; vertical-align: middle;'></span>
                    <span style='color: #3B4B5E; font-size: 0.85rem;'>Dia de hoje</span>
                </div>
                <div style='margin: 8px 0;'>
                    <span style='display: inline-block; width: 16px; height: 16px; 
                                 background-color: #FFFFFF; border: 2px solid #D4FF33; 
                                 border-radius: 4px; margin-right: 8px; vertical-align: middle;'></span>
                    <span style='color: #3B4B5E; font-size: 0.85rem;'>Dia com eventos</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar eventos do dia selecionado (opcional)
        if len(df_filtrado) > 0:
            st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
            st.markdown("### 📋 Eventos do Mês")
            
            # Filtrar eventos do mês
            eventos_mes = df_filtrado[
                (df_filtrado['Data início'].dt.month == mes_cal) &
                (df_filtrado['Data início'].dt.year == ano_cal)
            ].sort_values('Data início')
            
            if len(eventos_mes) > 0:
                for _, evento in eventos_mes.iterrows():
                    color, tipo_class = get_event_color(evento['Tipo de evento'])
                    tag_class = get_event_tag_class(evento['Tipo de evento'])
                    
                    data_inicio = evento['Data início']
                    data_fim = evento['Data Final']
                    
                    if pd.notna(data_inicio):
                        data_inicio_str = data_inicio.strftime('%d/%m')
                    else:
                        data_inicio_str = '--'
                    
                    if pd.notna(data_fim) and data_fim != data_inicio:
                        data_fim_str = " - " + data_fim.strftime('%d/%m')
                    else:
                        data_fim_str = ""
                    
                    tipo_evento_display = evento['Tipo de evento'] if pd.notna(evento['Tipo de evento']) else 'Não definido'
                    
                    st.markdown(f"""
                    <div style='background-color: #FFFFFF; border-left: 4px solid {color};
                                padding: 12px 16px; margin-bottom: 8px; border-radius: 8px;
                                box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='font-weight: 600; color: #3B4B5E; font-size: 0.95rem;'>
                                    {evento['Nome']}
                                </span>
                            </div>
                            <div>
                                <span class='event-tag {tag_class}'>{tipo_evento_display}</span>
                                <span style='color: #6B7A8F; font-size: 0.85rem; margin-left: 8px;'>
                                    {data_inicio_str}{data_fim_str}
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum evento neste mês.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6B7A8F; padding: 24px 0;'>
        <strong>blūmi talents</strong> | Transformando a contratação de jovens talentos<br>
        <span style='font-size: 0.85rem;'>@blumi_talents</span>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
